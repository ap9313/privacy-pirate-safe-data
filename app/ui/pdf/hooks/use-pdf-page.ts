"use client";

import { useEffect, useMemo, useState } from "react";

import { blurDocument } from "@/app/services/backend";

const samplePdfUrl = new URL("./sample.pdf", import.meta.url).toString();

export function usePdfPageState() {
  const [privacyLocked, setPrivacyLocked] = useState(false);
  const [privacyCoefficient, setPrivacyCoefficient] = useState(50);
  const [pdfFile, setPdfFile] = useState<File | string | null>(null);
  const [pdfProcessed, setPdfProcessed] = useState(false);
  const [pdfZoom, setPdfZoom] = useState(100);
  const [processedPdf, setProcessedPdf] = useState<{ url: string; filename: string } | null>(null);
  const [metadata, setMetadata] = useState<Record<string, unknown> | null>(null);
  const [processing, setProcessing] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);

  const handlePdfUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setPdfFile(file);
      setPdfProcessed(false);
      revokeProcessedPdf();
    }
  };

  const fillPdfExample = () => {
    setPdfFile(samplePdfUrl);
    setPdfProcessed(false);
    revokeProcessedPdf();
  };

  const cancelPdf = () => {
    setPdfFile(null);
    setPdfProcessed(false);
    setMetadata(null);
    setProcessingError(null);
    revokeProcessedPdf();
  };

  const revokeProcessedPdf = () => {
    setProcessedPdf((current) => {
      if (current) {
        URL.revokeObjectURL(current.url);
      }
      return null;
    });
  };

  useEffect(() => {
    return () => {
      revokeProcessedPdf();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const epsilon = useMemo(() => {
    const normalized = Math.max(10, Math.min(privacyCoefficient, 100));
    return Number((normalized / 50).toFixed(2));
  }, [privacyCoefficient]);

  const processPdf = async () => {
    if (!pdfFile || processing) {
      return;
    }
    setProcessing(true);
    setProcessingError(null);
    setPdfProcessed(false);
    setMetadata(null);
    try {
      let fileToSend: File;
      if (typeof pdfFile === "string") {
        const response = await fetch(pdfFile);
        if (!response.ok) {
          throw new Error("Failed to download sample PDF");
        }
        const blob = await response.blob();
        fileToSend = new File([blob], "sample.pdf", { type: blob.type || "application/pdf" });
      } else {
        fileToSend = pdfFile;
      }

      const result = await blurDocument(fileToSend, epsilon);
      revokeProcessedPdf();
      const url = URL.createObjectURL(result.blob);
      setProcessedPdf({ url, filename: result.filename });
      setPdfProcessed(true);
      setMetadata(result.metadata ?? null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to process PDF";
      setProcessingError(message);
    } finally {
      setProcessing(false);
    }
  };

  const downloadProcessedPdf = () => {
    if (!processedPdf) {
      return;
    }
    const link = document.createElement("a");
    link.href = processedPdf.url;
    link.download = processedPdf.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return {
    privacyLocked,
    setPrivacyLocked,
    privacyCoefficient,
    setPrivacyCoefficient,
    pdfFile,
    setPdfFile,
    pdfProcessed,
    setPdfProcessed,
    pdfZoom,
    setPdfZoom,
    handlePdfUpload,
    fillPdfExample,
    cancelPdf,
    processPdf,
    processedPdf,
    metadata,
    processing,
    processingError,
    downloadProcessedPdf,
  };
}
