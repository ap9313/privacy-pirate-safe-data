"use client";

import { useMemo, useState } from "react";

import { processFormPayload } from "@/app/services/backend";

export type FormFields = Record<string, string> & {
  name: string;
  gender: string;
  address: string;
  hobbies: string;
};

export function useFormPageState() {
  const [formData, setFormData] = useState<FormFields>({
    name: "",
    gender: "",
    address: "",
    hobbies: "",
  });
  const [formProcessed, setFormProcessed] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);
  const [processedResult, setProcessedResult] = useState<object | null>(null);
  const [privacyLocked, setPrivacyLocked] = useState(false);
  const [privacyCoefficient, setPrivacyCoefficient] = useState(50);

  const epsilon = useMemo(() => {
    const normalized = Math.max(10, Math.min(privacyCoefficient, 100));
    return Number((normalized / 50).toFixed(2));
  }, [privacyCoefficient]);

  const handleFormChange = (field: keyof FormFields, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setFormProcessed(false);
    setProcessedResult(null);
    setProcessingError(null);
  };

  const fillFormExample = () => {
    setFormData({
      name: "John Smith",
      gender: "Male",
      address: "123 Main Street, New York, NY 10001",
      hobbies: "Reading, Hiking, Photography",
    });
    setFormProcessed(false);
    setProcessedResult(null);
    setProcessingError(null);
  };

  const cancelForm = () => {
    setFormData({ name: "", gender: "", address: "", hobbies: "" });
    setFormProcessed(false);
    setProcessedResult(null);
    setProcessingError(null);
  };

  const processForm = async () => {
    setProcessing(true);
    setProcessingError(null);
    setFormProcessed(false);
    try {
      const result = await processFormPayload(formData, epsilon);
      setProcessedResult(result);
      setFormProcessed(true);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to process form";
      setProcessingError(message);
      setProcessedResult(null);
      setFormProcessed(false);
    } finally {
      setProcessing(false);
    }
  };

  return {
    formData,
    formProcessed,
    processedResult,
    processing,
    processingError,
    privacyLocked,
    privacyCoefficient,
    setFormProcessed,
    setPrivacyLocked,
    setPrivacyCoefficient,
    handleFormChange,
    fillFormExample,
    cancelForm,
    processForm,
  };
}
