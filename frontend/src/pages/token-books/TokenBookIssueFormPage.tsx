import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import {
  useTokenBookIssue,
  useCreateTokenBookIssue,
  useUpdateTokenBookIssue,
  useTokenBookIssues,
  useTokenIdentities,
} from "../../hooks/useTokenBooks";
import { BOOK_ISSUE_STATUS } from "../../lib/constants";

export default function TokenBookIssueFormPage() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { data: issue, isLoading } = useTokenBookIssue(Number(id));
  const { data: issues } = useTokenBookIssues();
  const { data: identities } = useTokenIdentities();
  const createIssue = useCreateTokenBookIssue();
  const updateIssue = useUpdateTokenBookIssue();

  const [form, setForm] = useState({
    token_identity_id: "",
    issue_number: "",
    status: "WAITING",
    current_sheet: "0",
    completion_date: "",
    remarks: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (issue) {
      setForm({
        token_identity_id: String(issue.token_identity.id),
        issue_number: String(issue.issue_number),
        status: issue.status,
        current_sheet: String(issue.current_sheet),
        completion_date: issue.completion_date ?? "",
        remarks: issue.remarks ?? "",
      });
    }
  }, [issue]);

  const activeIssueIds = new Set(
    (issues ?? []).filter((i) => i.status === "ACTIVE").map((i) => i.token_identity_id)
  );
  const availableIdentities = isEdit
    ? identities ?? []
    : (identities ?? []).filter((i) => !activeIssueIds.has(i.id));

  function validate() {
    const e: Record<string, string> = {};
    if (!form.token_identity_id || form.token_identity_id === "0") {
      e.token_identity_id = "Identity is required";
    }
    const issueNo = Number(form.issue_number);
    if (form.issue_number === "" || isNaN(issueNo) || issueNo <= 0 || !Number.isInteger(issueNo)) {
      e.issue_number = "Issue number must be a positive whole number";
    }
    const sheet = Number(form.current_sheet);
    if (isEdit && (form.current_sheet === "" || isNaN(sheet) || sheet < 0 || !Number.isInteger(sheet))) {
      e.current_sheet = "Current sheet must be 0 or a positive whole number";
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    try {
      if (isEdit) {
        await updateIssue.mutateAsync({
          id: Number(id),
          data: {
            status: form.status as any,
            current_sheet: Number(form.current_sheet),
            completion_date: form.completion_date || null,
            remarks: form.remarks || null,
          },
        });
      } else {
        await createIssue.mutateAsync({
          token_identity_id: Number(form.token_identity_id),
          issue_number: Number(form.issue_number),
          remarks: form.remarks || null,
        });
      }
      navigate("/token-book-issues");
    } catch {}
  }

  if (isEdit && isLoading) return <LoadingSpinner className="mt-20" />;

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-xl font-semibold text-slate-800 mb-6">
        {isEdit ? "Edit Token Book Issue" : "Create Token Book Issue"}
      </h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
        <Select
          label="Identity"
          required
          options={availableIdentities.map((i) => ({
            value: i.id,
            label: `#${i.token_number} - ${i.customer_name} (${i.milk_type_name})`,
          }))}
          placeholder={isEdit ? undefined : "Select an identity (without an active book)"}
          value={form.token_identity_id}
          onChange={(e) => setForm({ ...form, token_identity_id: e.target.value })}
          disabled={isEdit}
          error={errors.token_identity_id}
        />
        <Input
          label="Issue Number"
          required
          type="number"
          min={1}
          step={1}
          value={form.issue_number}
          onChange={(e) => setForm({ ...form, issue_number: e.target.value })}
          disabled={isEdit}
          error={errors.issue_number}
        />
        {isEdit && (
          <>
            <Select
              label="Status"
              options={Object.entries(BOOK_ISSUE_STATUS).map(([value, conf]) => ({
                value,
                label: conf.label,
              }))}
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            />
            <Input
              label="Current Sheet"
              type="number"
              min={0}
              step={1}
              value={form.current_sheet}
              onChange={(e) => setForm({ ...form, current_sheet: e.target.value })}
              error={errors.current_sheet}
            />
            <Input
              label="Completion Date"
              type="date"
              value={form.completion_date}
              onChange={(e) => setForm({ ...form, completion_date: e.target.value })}
            />
          </>
        )}
        <Textarea
          label="Remarks"
          value={form.remarks}
          onChange={(e) => setForm({ ...form, remarks: e.target.value })}
        />
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => navigate("/token-book-issues")}>
            Cancel
          </Button>
          <Button type="submit" loading={createIssue.isPending || updateIssue.isPending}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
