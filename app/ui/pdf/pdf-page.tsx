"use client";

import { Button } from "@/components/ui/button";
import dynamic from "next/dynamic";
import { AlertCircle, Upload, ZoomIn, ZoomOut } from "lucide-react";

import { ButtonRow } from "@/app/ui/common/button-row";
import { JsonViewer } from "@/app/ui/common/json-viewer";
import { usePdfPageState } from "@/app/ui/pdf/hooks/use-pdf-page";

const PdfViewer = dynamic(() => import("@/components/pdf-viewer"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-40 text-muted-foreground">
      Loading PDF viewer...
    </div>
  ),
});

export function PdfPage() {
  const {
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
  } = usePdfPageState();

  return (
    <div className="p-6 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-primary mb-4">PDF Processing</h2>
      <ButtonRow
        onProcess={processPdf}
        processDisabled={!pdfFile}
        processing={processing}
        onCancel={cancelPdf}
        onFillExample={fillPdfExample}
        showDownload
        downloadDisabled={!pdfProcessed || !processedPdf}
        onDownload={downloadProcessedPdf}
        privacyLocked={privacyLocked}
        privacyCoefficient={privacyCoefficient}
        onPrivacyLockChange={setPrivacyLocked}
        onPrivacyChange={setPrivacyCoefficient}
      />
      <div className="flex items-center gap-4 mb-4 p-3 bg-card border border-border rounded-lg">
        <span className="text-sm font-medium text-foreground">Zoom:</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPdfZoom(Math.max(50, pdfZoom - 25))}
          disabled={pdfZoom <= 50}
          className="bg-transparent"
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <span className="text-sm font-mono w-12 text-center text-foreground">{pdfZoom}%</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPdfZoom(Math.min(200, pdfZoom + 25))}
          disabled={pdfZoom >= 200}
          className="bg-transparent"
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
      </div>
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
        <div className="flex flex-col min-h-0">
          <h3 className="font-semibold mb-2 text-foreground">Original PDF</h3>
          <div className="flex-1 border-2 border-dashed border-border rounded-lg overflow-hidden bg-muted min-h-[600px]">
            {pdfFile ? (
              <PdfViewer file={pdfFile} rotated={false} width={Math.round(500 * (pdfZoom / 100))} />
            ) : (
              <label className="cursor-pointer flex flex-col items-center justify-center h-full p-4">
                <Upload className="w-12 h-12 mb-2 text-muted-foreground" />
                <p className="text-muted-foreground">Click to upload PDF</p>
                <input type="file" accept=".pdf" onChange={handlePdfUpload} className="hidden" />
              </label>
            )}
          </div>
        </div>
        <div className="flex flex-col min-h-0">
          <h3 className="font-semibold mb-2 text-foreground">Processed PDF</h3>
          <div className="flex-1 border border-border rounded-lg overflow-hidden bg-muted min-h-[600px]">
            {pdfProcessed && processedPdf ? (
              <PdfViewer file={processedPdf.url} rotated={false} width={Math.round(500 * (pdfZoom / 100))} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">Process a PDF to see results</p>
              </div>
            )}
          </div>
          {processingError && (
            <div className="mt-4 flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="w-4 h-4" />
              <span>{processingError}</span>
            </div>
          )}
        </div>
      </div>
      {metadata && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold mb-2 text-foreground">Metadata</h4>
          <div className="max-h-[300px] overflow-auto">
            <JsonViewer data={metadata} />
          </div>
        </div>
      )}
    </div>
  );
}
