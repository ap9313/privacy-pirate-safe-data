"use client";

import { cn } from "@/lib/utils";

interface JsonViewerProps {
  data: object;
  className?: string;
  height?: "auto" | "full" | "fixed";
}

export function JsonViewer({ data, className, height = "auto" }: JsonViewerProps) {
  const heightClass =
    height === "full"
      ? "h-full"
      : height === "fixed"
        ? "h-[360px]"
        : "min-h-[200px]";

  return (
    <div
      className={cn(
        "bg-[#f5e6d3] text-[#5c4033] p-4 rounded-lg font-mono text-sm overflow-auto border border-[#d4a574]",
        heightClass,
        className,
      )}
    >
      <pre className="whitespace-pre-wrap break-words">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
