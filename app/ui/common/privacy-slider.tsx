"use client";

import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface PrivacySliderProps {
  locked: boolean;
  coefficient: number;
  onToggleLock: (value: boolean) => void;
  onChange: (value: number) => void;
}

export function PrivacySlider({
  locked,
  coefficient,
  onToggleLock,
  onChange,
}: PrivacySliderProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-foreground">Lock slider</span>
        <Switch checked={locked} onCheckedChange={onToggleLock} />
      </div>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-2 flex-1 max-w-md">
              <div className="flex items-center gap-2 flex-1">
                <span className="text-xs tracking-wide text-muted-foreground whitespace-nowrap">
                  Low utility
                </span>
                <Slider
                  value={[coefficient]}
                  onValueChange={(value) => onChange(value[0])}
                  min={0}
                  max={100}
                  step={1}
                  disabled={locked}
                  className="flex-1"
                />
                <span className="text-xs tracking-wide text-muted-foreground whitespace-nowrap">
                  High utility
                </span>
              </div>
              <span className="text-sm font-mono w-12 text-foreground">{coefficient}%</span>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <p>
              <strong>Privacy Coefficient:</strong>
              <br />
              100% = High utility, low privacy for recommender systems
              <br />
              0% = High privacy, low utility
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
}
