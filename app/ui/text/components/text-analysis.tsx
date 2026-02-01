import { Textarea } from "@/components/ui/textarea";

import { JsonViewer } from "@/app/ui/common/json-viewer";

interface TextAnalysisProps {
  textContent: string;
  onChange: (value: string) => void;
  extractedData: object;
  error?: string | null;
}

export function TextAnalysis({ textContent, onChange, extractedData, error }: TextAnalysisProps) {
  return (
    <div className="flex-1 grid grid-cols-1 gap-6 items-start lg:grid-cols-2">
      <div className="flex flex-col space-y-2">
        <h3 className="font-semibold text-foreground">Input Text</h3>
        <Textarea
          value={textContent}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Enter or paste text containing personal information..."
          className="h-[360px] resize-none"
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>
      <div className="flex flex-col space-y-2">
        <h3 className="font-semibold text-foreground">Extracted Data (JSON)</h3>
        <JsonViewer data={extractedData} height="fixed" />
      </div>
    </div>
  );
}
