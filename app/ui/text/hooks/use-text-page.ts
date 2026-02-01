import { useMemo, useState } from "react";

import { processTextPayload } from "@/app/services/backend";

export function useTextPageState() {
  const [textContent, setTextContent] = useState("");
  const [textProcessed, setTextProcessed] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);
  const [processedResult, setProcessedResult] = useState<object | null>(null);
  const [privacyLocked, setPrivacyLocked] = useState(false);
  const [privacyCoefficient, setPrivacyCoefficient] = useState(50);

  const epsilon = useMemo(() => {
    const normalized = Math.max(10, Math.min(privacyCoefficient, 100));
    return Number((normalized / 50).toFixed(2));
  }, [privacyCoefficient]);

  const fillTextExample = () => {
    setTextContent(
      `John Smith is a 34-year-old software engineer living at 456 Oak Avenue, San Francisco, CA 94102. He graduated from Stanford University in 2012 with a degree in Computer Science. John enjoys hiking in the nearby mountains and often visits Yosemite National Park during weekends.

His email address is john.smith@techcompany.com and his phone number is (415) 555-0123. John has been working at TechCorp Inc. for the past 5 years, where he leads a team of developers. He is known for his expertise in machine learning and has published several papers on privacy-preserving data analysis.`
    );
    setProcessedResult(null);
    setProcessingError(null);
    setTextProcessed(false);
  };

  const cancelText = () => {
    setTextContent("");
    setProcessedResult(null);
    setProcessingError(null);
    setTextProcessed(false);
  };

  const processText = async () => {
    if (!textContent.trim()) {
      setProcessingError("Please enter some text before processing.");
      return;
    }

    setProcessing(true);
    setProcessingError(null);
    setTextProcessed(false);
    try {
      const result = await processTextPayload(textContent, epsilon);
      setProcessedResult(result);
      setTextProcessed(true);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to process text";
      setProcessingError(message);
      setProcessedResult(null);
      setTextProcessed(false);
    } finally {
      setProcessing(false);
    }
  };

  const handleTextChange = (value: string) => {
    setTextContent(value);
    setTextProcessed(false);
    setProcessedResult(null);
    setProcessingError(null);
  };

  return {
    textContent,
    setTextContent: handleTextChange,
    textProcessed,
    setTextProcessed,
    processedResult,
    processing,
    processingError,
    privacyLocked,
    setPrivacyLocked,
    privacyCoefficient,
    setPrivacyCoefficient,
    fillTextExample,
    cancelText,
    processText,
  };
}
