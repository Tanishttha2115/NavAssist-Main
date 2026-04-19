import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Shield, Skull } from "lucide-react";
import { useLang } from "@/contexts/LangContext";
import type { DetectedObject } from "@/lib/api";

interface Props {
  objects: DetectedObject[];
}

const DetectionAlerts: React.FC<Props> = ({ objects }) => {
  const { t } = useLang();

  const severityConfig = {
    safe: { icon: Shield, bg: "bg-safe/15", border: "border-safe/30", text: "text-safe", label: t.safe },
    warning: { icon: AlertTriangle, bg: "bg-warning/15", border: "border-warning/30", text: "text-warning", label: t.warning },
    danger: { icon: Skull, bg: "bg-danger/15", border: "border-danger/30", text: "text-danger", label: t.danger },
  };

  const directionAdvice = (pos: string) => {
    if (pos === "center") return t.dirStop;
    if (pos === "left") return t.dirMoveRight;
    if (pos === "right") return t.dirMoveLeft;
    return "";
  };

  if (!objects.length) return null;

  return (
    <div className="space-y-3" role="alert" aria-live="assertive">
      <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider px-1">{t.detection}</h3>
      <AnimatePresence mode="popLayout">
        {objects.map((obj, i) => {
          const severity = (["safe", "warning", "danger"] as const).includes(obj?.severity as any)
            ? obj.severity
            : "warning";
          const position = obj?.position ?? "center";
          const label = obj?.label ?? "Object";
          const cfg = severityConfig[severity];
          const Icon = cfg.icon;
          return (
            <motion.div
              key={`${label}-${position}-${i}`}
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`flex items-center gap-4 p-4 rounded-2xl border-2 ${cfg.bg} ${cfg.border}`}
            >
              <Icon className={`w-6 h-6 ${cfg.text}`} />
              <div className="flex-1">
                <p className="text-base font-semibold text-foreground">{label}</p>
                <p className={`text-sm font-medium ${cfg.text}`}>{directionAdvice(position)}</p>
              </div>
              <span className={`text-xs font-bold uppercase ${cfg.text}`}>{cfg.label}</span>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};

export default DetectionAlerts;
