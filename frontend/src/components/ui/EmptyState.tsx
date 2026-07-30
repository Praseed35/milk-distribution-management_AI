import { cn } from "../../lib/utils";
import Button from "./Button";

interface EmptyStateProps {
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export default function EmptyState({ message, actionLabel, onAction, className }: EmptyStateProps) {
  return (
    <div className={cn("bg-white rounded-lg shadow p-12 text-center", className)}>
      <p className="text-slate-500 mb-4">{message}</p>
      {actionLabel && onAction && (
        <Button variant="secondary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
