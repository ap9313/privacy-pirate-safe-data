import re
import os
from gliner import GLiNER
from typing import List, Dict, Any
from app.config import (
    NER_MODEL_NAME,
    NER_LABELS,
    NER_THRESHOLD,
    SECRET_KEYWORDS,
    PII_REGEX_PATTERNS,
    DATA_DIR,
    GLINER_LOCAL_DIR,
    SCANNER_CHUNK_SIZE,
    SCANNER_CHUNK_OVERLAP
)


class Scanner:
    _model_instance = None

    def __init__(self):
        self._load_ner_model()
        self.labels = NER_LABELS
        self.threshold = NER_THRESHOLD

    def _load_ner_model(self):
        if Scanner._model_instance is not None:
            self.ner_model = Scanner._model_instance
            return

        print(f" [Scanner] Loading GLiNER model ({NER_MODEL_NAME})...")
        local_path = os.path.join(DATA_DIR, "models", GLINER_LOCAL_DIR)

        if os.path.exists(local_path):
            Scanner._model_instance = GLiNER.from_pretrained(local_path, local_files_only=True)
        else:
            print(" [Scanner] Local model not found. Downloading...")
            Scanner._model_instance = GLiNER.from_pretrained(NER_MODEL_NAME)

        self.ner_model = Scanner._model_instance

    def scan(self, text: str, chunk_size: int = SCANNER_CHUNK_SIZE, overlap: int = SCANNER_CHUNK_OVERLAP) -> List[Dict]:
        """
        Processes long text by splitting it into overlapping chunks.
        Combines NER (GLiNER) findings with Regex findings.
        """
        words = text.split()
        all_findings = []

        if len(words) <= chunk_size:
            all_findings.extend(self._run_model_on_text(text))
        else:
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i: i + chunk_size]
                chunk_text = " ".join(chunk_words)

                start_char_offset = len(" ".join(words[:i])) + (1 if i > 0 else 0)

                chunk_findings = self._run_model_on_text(chunk_text)

                for f in chunk_findings:
                    f['start'] += start_char_offset
                    f['end'] += start_char_offset
                    f['source'] = "GLiNER"
                    all_findings.append(f)

        secret_findings = self._scan_for_secrets(text)
        all_findings.extend(secret_findings)

        return self._deduplicate_findings(all_findings)

    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """
        Removes exact duplicates and handles overlapping entities
        (e.g., keeping the longest span or merging).
        """
        if not findings:
            return []

        sorted_f = sorted(findings, key=lambda x: (x['start'], -(x['end'] - x['start'])))
        unique_findings = []

        if sorted_f:
            current = sorted_f[0]
            for next_f in sorted_f[1:]:
                if next_f['start'] < current['end']:
                    if next_f.get('source') == 'Regex' and current.get('source') != 'Regex':
                        current = next_f
                    elif (next_f['end'] - next_f['start']) > (current['end'] - current['start']):
                        current = next_f
                else:
                    unique_findings.append(current)
                    current = next_f
            unique_findings.append(current)

        return unique_findings

    def _run_model_on_text(self, text: str) -> List[Dict]:
        if not text.strip(): return []
        entities = self.ner_model.predict_entities(text, self.labels, threshold=self.threshold)
        return [{
            "text": e["text"], "label": e["label"], "score": float(e["score"]),
            "start": e["start"], "end": e["end"]
        } for e in entities]

    def _scan_for_secrets(self, text: str) -> List[Dict]:
        """
        Uses regex patterns from config to find actual secret values.
        """
        findings = []
        for pattern, label in PII_REGEX_PATTERNS:
            for match in re.finditer(pattern, text):
                findings.append({
                    "text": match.group(),
                    "label": label,
                    "score": 1.0,
                    "source": "Regex",
                    "start": match.start(),
                    "end": match.end()
                })

        return findings

    def create_boomerang_map(self, findings: List[Dict]) -> Dict[str, str]:
        """Creates map: 'John Smith' -> '<PERSON_1>'"""
        entity_map = {}
        counts = {}
        sorted_findings = sorted(findings, key=lambda x: len(x['text']), reverse=True)
        for f in sorted_findings:
            original = f['text']
            label = f['label'].upper().replace(" ", "_")
            if label == "SECURITY_SECRET":
                continue

            if original not in entity_map:
                if label not in counts: counts[label] = 0
                counts[label] += 1
                entity_map[original] = f"<{label}_{counts[label]}>"

        return entity_map

    def restore_from_map(self, text: str, entity_map: Dict[str, str]) -> str:
        """Restores Real Data"""
        for original, tag in entity_map.items():
            text = text.replace(tag, original)
        return text

    def redact(self, text: str, findings: List[Dict]) -> str:
        if not findings:
            return text

        # FIX: Generate the unique tags map first!
        entity_map = self.create_boomerang_map(findings)

        sorted_findings = sorted(findings, key=lambda x: x['start'])
        non_overlapping = []
        last_end = -1

        for f in sorted_findings:
            if f['start'] >= last_end:
                non_overlapping.append(f)
                last_end = f['end']
            else:
                if f['end'] > last_end:
                    if len(non_overlapping) > 0 and f['start'] <= non_overlapping[-1]['start']:
                        non_overlapping.pop()
                    non_overlapping.append(f)
                    last_end = f['end']

        safe_text = text
        for f in reversed(non_overlapping):
            start, end = f['start'], f['end']
            replacement = entity_map.get(f['text'])
            if not replacement:
                label = f['label'].upper().replace(" ", "_")
                replacement = f"<{label}>"

            if start < 0 or end > len(safe_text): continue
            safe_text = safe_text[:start] + replacement + safe_text[end:]
        return safe_text