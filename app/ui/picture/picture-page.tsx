"use client";

import { Upload } from "lucide-react";

import { ButtonRow } from "@/app/ui/common/button-row";
import { JsonViewer } from "@/app/ui/common/json-viewer";
import { usePicturePageState } from "@/app/ui/picture/hooks/use-picture-page";

export function PicturePage() {
  const {
    privacyLocked,
    setPrivacyLocked,
    privacyCoefficient,
    setPrivacyCoefficient,
    pictureFile,
    pictureUrl,
    pictureProcessed,
    processedUrl,
    processing,
    error,
    metadata,
    handlePictureUpload,
    fillPictureExample,
    cancelPicture,
    processPicture,
  } = usePicturePageState();

  return (
    <div className="p-6 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-primary mb-4">Image Processing</h2>
      <ButtonRow
        onProcess={processPicture}
        processDisabled={!pictureUrl}
        processing={processing}
        onCancel={cancelPicture}
        onFillExample={fillPictureExample}
        showDownload
        downloadDisabled={!pictureProcessed || !processedUrl}
        onDownload={() => {
          if (!processedUrl) return;
          const link = document.createElement("a");
          link.href = processedUrl;
          link.download = "blurred-image.png";
          link.click();
        }}
        privacyLocked={privacyLocked}
        privacyCoefficient={privacyCoefficient}
        onPrivacyLockChange={setPrivacyLocked}
        onPrivacyChange={setPrivacyCoefficient}
      />
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex flex-col">
          <h3 className="font-semibold mb-2 text-foreground">Original Image</h3>
          <div className="flex-1 border-2 border-dashed border-border rounded-lg flex items-center justify-center bg-muted min-h-[400px] overflow-hidden">
            {pictureUrl ? (
              <img src={pictureUrl || "/placeholder.svg"} alt="Original" className="max-w-full max-h-full object-contain" crossOrigin="anonymous" />
            ) : (
              <label className="cursor-pointer text-center p-4">
                <Upload className="w-12 h-12 mx-auto mb-2 text-muted-foreground" />
                <p className="text-muted-foreground">Click to upload image</p>
                <input type="file" accept="image/*" onChange={handlePictureUpload} className="hidden" />
              </label>
            )}
          </div>
        </div>
        <div className="flex flex-col">
          <h3 className="font-semibold mb-2 text-foreground">Processed Image</h3>
          <div className="flex-1 border border-border rounded-lg flex items-center justify-center bg-muted min-h-[400px] overflow-hidden">
            {processing ? (
              <p className="text-muted-foreground">Processing image…</p>
            ) : pictureProcessed && processedUrl ? (
              <img
                src={processedUrl}
                alt="Processed"
                className="max-w-full max-h-full object-contain"
                crossOrigin="anonymous"
              />
            ) : (
              <p className="text-muted-foreground">Process an image to see results</p>
            )}
          </div>
          {error && <p className="text-sm text-destructive mt-2">{error}</p>}
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
