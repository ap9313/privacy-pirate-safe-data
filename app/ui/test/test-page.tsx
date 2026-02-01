"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

import { fetchBackendStatus, STATUS_ENDPOINT } from "@/app/services/backend";

export function TestPage() {
  const [testStatus, setTestStatus] = useState<{ status: string; message: string } | null>(null);
  const [testLoading, setTestLoading] = useState(false);

  const testBackendConnection = async () => {
    setTestLoading(true);
    setTestStatus(null);
    try {
      const data = await fetchBackendStatus();
      setTestStatus(data);
    } catch {
      setTestStatus({ status: "error", message: `Failed to connect to backend at ${STATUS_ENDPOINT}` });
    }
    setTestLoading(false);
  };

  return (
    <div className="p-8 max-w-2xl mx-auto flex flex-col items-center justify-center min-h-[60vh]">
      <h2 className="text-2xl font-bold text-primary mb-6">Backend Connection Test</h2>
      <p className="text-muted-foreground mb-8 text-center">
        Click the button below to test the connection to the Flask backend at <code className="bg-muted px-2 py-1 rounded">{STATUS_ENDPOINT}</code>
      </p>
      <Button onClick={testBackendConnection} disabled={testLoading} size="lg" className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-6 text-lg">
        {testLoading ? "Testing..." : "Test Connection"}
      </Button>
      {testStatus && (
        <div
          className={`mt-8 px-8 py-5 rounded-lg text-center w-full max-w-md ${
            ["ok", "online", "success"].includes(testStatus.status?.toLowerCase?.() ?? "")
              ? "bg-[rgba(34,197,94,0.15)] border border-[rgba(34,197,94,0.3)]"
              : "bg-[rgba(239,68,68,0.15)] border border-[rgba(239,68,68,0.3)]"
          }`}
        >
          <p className="my-2 text-foreground">
            <strong>Status:</strong> {testStatus.status}
          </p>
          <p className="my-2 text-foreground">
            <strong>Message:</strong> {testStatus.message}
          </p>
        </div>
      )}
    </div>
  );
}
