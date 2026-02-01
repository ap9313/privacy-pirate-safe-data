"use client";

import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

import { ButtonRow } from "@/app/ui/common/button-row";
import { JsonViewer } from "@/app/ui/common/json-viewer";

import { useFormPageState } from "@/app/ui/form/hooks/use-form-page";

export function FormPage() {
  const {
    formData,
    formProcessed,
    processedResult,
    processing,
    processingError,
    privacyLocked,
    privacyCoefficient,
    setPrivacyLocked,
    setPrivacyCoefficient,
    handleFormChange,
    fillFormExample,
    cancelForm,
    processForm,
  } = useFormPageState();

  return (
    <div className="p-6 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-primary mb-4">Form Data Entry</h2>
      <ButtonRow
        onProcess={processForm}
        processing={processing}
        onCancel={cancelForm}
        onFillExample={fillFormExample}
        privacyLocked={privacyLocked}
        privacyCoefficient={privacyCoefficient}
        onPrivacyLockChange={setPrivacyLocked}
        onPrivacyChange={setPrivacyCoefficient}
      />
      <div className="flex-1 grid grid-cols-1 gap-6 items-start lg:grid-cols-2">
        <div className="flex flex-col space-y-2">
          <h3 className="font-semibold text-foreground">Personal Information</h3>
          <div className="h-[360px] space-y-4 overflow-auto pr-2">
            <div>
              <label className="block text-sm font-medium mb-1 text-foreground">Name</label>
              <Input
                value={formData.name}
                onChange={(e) => handleFormChange("name", e.target.value)}
                placeholder="Enter full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-foreground">Gender</label>
              <Select
                value={formData.gender}
                onValueChange={(value) => handleFormChange("gender", value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Female">Female</SelectItem>
                  <SelectItem value="Male">Male</SelectItem>
                  <SelectItem value="Non-binary">Non-binary</SelectItem>
                  <SelectItem value="Prefer not to say">Prefer not to say</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-foreground">Address</label>
              <Textarea
                value={formData.address}
                onChange={(e) => handleFormChange("address", e.target.value)}
                placeholder="Enter full address"
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-foreground">Hobbies</label>
              <Textarea
                value={formData.hobbies}
                onChange={(e) => handleFormChange("hobbies", e.target.value)}
                placeholder="Enter hobbies"
                rows={3}
              />
            </div>
          </div>
        </div>
        <div className="flex flex-col space-y-2">
          <h3 className="font-semibold text-foreground">JSON Output</h3>
          <JsonViewer
            data={formProcessed && processedResult ? processedResult : formData}
            height="fixed"
          />
          {processingError && <p className="text-sm text-destructive">{processingError}</p>}
        </div>
      </div>
    </div>
  );
}
