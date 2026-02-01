"use client";

import { useState, useCallback } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PdfViewerProps {
  file: File | string | null;
  rotated?: boolean;
  width?: number;
}

export default function PdfViewer({ file, rotated = false, width = 400 }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null);

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  }, []);

  if (!file) {
    return null;
  }

  return (
    <div className="overflow-auto h-full w-full flex flex-col items-center bg-neutral-100 dark:bg-neutral-900 p-4 rounded-lg">
      <Document
        file={file}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={
          <div className="flex items-center justify-center h-40">
            <p className="text-muted-foreground">Loading PDF...</p>
          </div>
        }
        error={
          <div className="flex items-center justify-center h-40">
            <p className="text-destructive">Failed to load PDF</p>
          </div>
        }
      >
        {numPages &&
          Array.from(new Array(numPages), (_, index) => (
            <div
              key={`page_${index + 1}`}
              className="mb-4 shadow-lg"
              style={rotated ? { transform: "rotate(180deg)" } : undefined}
            >
              <Page
                pageNumber={index + 1}
                width={width}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </div>
          ))}
      </Document>
      {numPages && (
        <p className="text-sm text-muted-foreground mt-2">
          {numPages} page{numPages > 1 ? "s" : ""}
        </p>
      )}
    </div>
  );
}
