"use client";

import { ButtonRow } from "@/app/ui/common/button-row";

import { TextAnalysis } from "@/app/ui/text/components/text-analysis";
import { useTextPageState } from "@/app/ui/text/hooks/use-text-page";

export function TextPage() {
  const {
    textContent,
    setTextContent,
    textProcessed,
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
  } = useTextPageState();

  const extractedData = textProcessed && processedResult ? processedResult : { message: "Process text to view results" };

  return (
    <div className="p-6 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-primary mb-4">Text Analysis</h2>
      <ButtonRow
        onProcess={processText}
        processing={processing}
        onCancel={cancelText}
        onFillExample={fillTextExample}
        privacyLocked={privacyLocked}
        privacyCoefficient={privacyCoefficient}
        onPrivacyLockChange={setPrivacyLocked}
        onPrivacyChange={setPrivacyCoefficient}
      />
      <TextAnalysis
        textContent={textContent}
        onChange={(value) => {
          setTextContent(value);
        }}
        extractedData={extractedData}
        error={processingError}
      />
    </div>
  );
}
