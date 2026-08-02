import Button from "../ui/Button";
import Input from "../ui/Input";
import Select from "../ui/Select";
import { REPORT_PRESETS } from "../../lib/constants";

interface PresetFilterProps {
  preset: string;
  fromDate: string;
  toDate: string;
  onPresetChange: (value: string) => void;
  onFromDateChange: (value: string) => void;
  onToDateChange: (value: string) => void;
  onRefresh?: () => void;
  showRefresh?: boolean;
}

export default function PresetFilter({
  preset,
  fromDate,
  toDate,
  onPresetChange,
  onFromDateChange,
  onToDateChange,
  onRefresh,
  showRefresh = true,
}: PresetFilterProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 items-end">
      <Select
        label="Period"
        options={REPORT_PRESETS.map((p) => ({ value: p.value, label: p.label }))}
        placeholder="Custom dates"
        value={preset}
        onChange={(e) => onPresetChange(e.target.value)}
      />
      <Input
        label="From"
        type="date"
        value={fromDate}
        disabled={!!preset}
        onChange={(e) => onFromDateChange(e.target.value)}
      />
      <Input
        label="To"
        type="date"
        value={toDate}
        disabled={!!preset}
        onChange={(e) => onToDateChange(e.target.value)}
      />
      {showRefresh ? (
        <Button variant="secondary" onClick={onRefresh}>
          Refresh
        </Button>
      ) : (
        <div />
      )}
    </div>
  );
}
