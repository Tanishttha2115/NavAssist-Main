import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowUp, CornerDownLeft, CornerDownRight, Navigation, CheckCircle } from "lucide-react";
import { useLang } from "@/contexts/LangContext";
import type { NavStep } from "@/lib/api";

interface Props {
  steps: NavStep[];
  currentStep: number;
  /** Distance (in meters) remaining to the end of the current step. */
  distanceToNext?: number | null;
}

const iconFor = (text?: string, maneuver?: string) => {
  const lower = ((text ?? "") + " " + (maneuver ?? "")).toLowerCase();
  if (lower.includes("बाएं") || lower.includes("left")) return <CornerDownLeft className="w-10 h-10" />;
  if (lower.includes("दाएं") || lower.includes("right")) return <CornerDownRight className="w-10 h-10" />;
  if (lower.includes("सीधे") || lower.includes("straight") || lower.includes("walk") || lower.includes("चल"))
    return <ArrowUp className="w-10 h-10" />;
  if (lower.includes("पहुँच") || lower.includes("arrived") || lower.includes("destination"))
    return <CheckCircle className="w-10 h-10" />;
  return <Navigation className="w-10 h-10" />;
};

const NavigationSteps: React.FC<Props> = ({ steps, currentStep, distanceToNext }) => {
  const { t } = useLang();

  if (!steps.length) return null;

  const step = steps[currentStep] ?? steps[steps.length - 1];
  const instruction =
    (step as any)?.instruction ||
    (step as any)?.text ||
    "—";
  const distanceLabel =
    typeof distanceToNext === "number" && isFinite(distanceToNext)
      ? `${Math.max(0, Math.round(distanceToNext))} ${t.meters}`
      : (step as any)?.distance_value
      ? `${Math.round((step as any).distance_value)} ${t.meters}`
      : (step as any)?.distance || "";

  return (
    <div className="space-y-3" aria-label={t.navigation}>
      <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider px-1">
        {t.navigation} · {currentStep + 1}/{steps.length}
      </h3>
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.25 }}
          role="status"
          aria-live="polite"
          className="flex items-center gap-5 p-6 rounded-3xl bg-primary/15 border-2 border-primary/40 text-foreground shadow-lg"
        >
          <div className="p-4 rounded-2xl bg-primary text-primary-foreground shrink-0">
            {iconFor(instruction, (step as any)?.maneuver || (step as any)?.type)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-2xl font-bold leading-tight">{instruction}</p>
            {distanceLabel && (
              <p className="text-lg text-muted-foreground font-semibold mt-1">{distanceLabel}</p>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default NavigationSteps;
