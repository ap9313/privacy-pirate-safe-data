"use client";

import { Button } from "@/components/ui/button";

import { PrivacySlider } from "./privacy-slider";

interface ButtonRowProps {
  onProcess: () => void;
  processDisabled?: boolean;
  processing?: boolean;
  onCancel: () => void;
  onFillExample: () => void;
  onDownload?: () => void;
  showDownload?: boolean;
  downloadDisabled?: boolean;
  privacyLocked: boolean;
  privacyCoefficient: number;
  onPrivacyLockChange: (value: boolean) => void;
  onPrivacyChange: (value: number) => void;
}

export function ButtonRow({
  onProcess,
  processDisabled = false,
  processing = false,
  onCancel,
  onFillExample,
  onDownload,
  showDownload = false,
  downloadDisabled = true,
  privacyLocked,
  privacyCoefficient,
  onPrivacyLockChange,
  onPrivacyChange,
}: ButtonRowProps) {
  return (
    <div className="flex flex-wrap items-center gap-4 p-4 bg-card border border-border rounded-lg mb-4">
      <div className="flex gap-2">
        <Button
          onClick={onProcess}
          disabled={processDisabled || processing}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          {processing ? "Processing…" : "Process"}
        </Button>
        <Button onClick={onCancel} variant="outline" className="border-border text-foreground hover:bg-muted bg-transparent">
          Cancel
        </Button>
        <Button onClick={onFillExample} variant="secondary" className="bg-secondary hover:bg-secondary/90 text-secondary-foreground">
          Fill Example
        </Button>
        {showDownload && (
          <Button
            onClick={onDownload}
            disabled={downloadDisabled}
            variant="outline"
            className="border-border text-foreground hover:bg-muted bg-transparent"
          >
            Download
          </Button>
        )}
      </div>
      <div className="flex-1 min-w-[300px]">
        <PrivacySlider
          locked={privacyLocked}
          coefficient={privacyCoefficient}
          onToggleLock={onPrivacyLockChange}
          onChange={onPrivacyChange}
        />
      </div>
    </div>
  );
}
