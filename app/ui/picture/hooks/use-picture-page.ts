"use client";

import { useState } from "react";
import { blurImage } from "@/app/services/backend";

export function usePicturePageState() {
  const [privacyLocked, setPrivacyLocked] = useState(false);
  const [privacyCoefficient, setPrivacyCoefficient] = useState(50);
  const [pictureFile, setPictureFile] = useState<File | null>(null);
  const [pictureUrl, setPictureUrl] = useState<string | null>(null);
  const [pictureProcessed, setPictureProcessed] = useState(false);
  const [processedUrl, setProcessedUrl] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<Record<string, unknown> | null>(null);

  const handlePictureUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setPictureFile(file);
      setPictureUrl(URL.createObjectURL(file));
      setPictureProcessed(false);
      setProcessedUrl(null);
      setError(null);
      setMetadata(null);
    }
  };

  const fillPictureExample = () => {
    setPictureUrl("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop");
    setPictureFile(null);
    setPictureProcessed(false);
    setProcessedUrl(null);
    setError(null);
    setMetadata(null);
  };

  const cancelPicture = () => {
    setPictureFile(null);
    setPictureUrl(null);
    setPictureProcessed(false);
    setProcessedUrl(null);
    setError(null);
    setMetadata(null);
  };

  const processPicture = async () => {
    if (!pictureUrl) {
      setError("Please upload an image or use the example first");
      return;
    }

    setProcessing(true);
    setError(null);
    setMetadata(null);

    try {
      let fileToProcess = pictureFile;

      if (!fileToProcess) {
        const response = await fetch(pictureUrl, { mode: "cors" });
        if (!response.ok) {
          throw new Error("Failed to download example image");
        }
        const blob = await response.blob();
        fileToProcess = new File([blob], "example-image.jpg", { type: blob.type || "image/jpeg" });
      }

      if (!fileToProcess) {
        throw new Error("Unable to determine image to process");
      }

      const { blob, metadata: responseMetadata } = await blurImage(fileToProcess);
      const blobUrl = URL.createObjectURL(blob);
      setProcessedUrl(blobUrl);
      setPictureProcessed(true);
      setMetadata(responseMetadata ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process image");
      setProcessedUrl(null);
      setPictureProcessed(false);
      setMetadata(null);
    } finally {
      setProcessing(false);
    }
  };

  return {
    privacyLocked,
    setPrivacyLocked,
    privacyCoefficient,
    setPrivacyCoefficient,
    pictureFile,
    setPictureFile,
    pictureUrl,
    setPictureUrl,
    pictureProcessed,
    setPictureProcessed,
    processedUrl,
    processing,
    error,
    metadata,
    handlePictureUpload,
    fillPictureExample,
    cancelPicture,
    processPicture,
  };
}
