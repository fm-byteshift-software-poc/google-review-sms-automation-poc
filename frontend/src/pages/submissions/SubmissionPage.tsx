import { useState, useEffect } from "react";
import { Send, RefreshCw, Clock, XCircle, CheckCircle, AlertTriangle, Copy } from "lucide-react";

const API_KEY = import.meta.env.VITE_API_KEY || "";
const BASE_URL = "/api";

type Submission = {
  id: string;
  first_name: string;
  phone_number: string;
  status: "pending" | "suppressed" | "satisfied" | "dissatisfied";
  suppression_reason: string | null;
  sms_sent: boolean;
  sms_sent_at: string | null;
  created_at: string;
};

export default function SubmissionPage() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({ first_name: "", phone_number: "" });
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchSubmissions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/submissions`, {
        headers: { "X-API-Key": API_KEY }
      });
      if (!res.ok) throw new Error("Failed to fetch submissions");
      const data = await res.json();
      setSubmissions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setMessage({ type: "error", text: "Failed to load submissions" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const payload = {
        ...formData,
        phone_number: formData.phone_number.startsWith("whatsapp:")
          ? formData.phone_number
          : `whatsapp:${formData.phone_number}`
      };

      const res = await fetch(`${BASE_URL}/submissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Request failed");
      setMessage({ type: "success", text: data.message });
      setFormData({ first_name: "", phone_number: "" });
      fetchSubmissions();
    } catch (err: any) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <span className="badge badge-warning gap-2"><Clock size={14} /> Pending</span>;
      case "suppressed":
        return <span className="badge badge-error gap-2"><XCircle size={14} /> Suppressed</span>;
      case "satisfied":
        return <span className="badge badge-success gap-2"><CheckCircle size={14} /> Satisfied</span>;
      case "dissatisfied":
        return <span className="badge badge-info gap-2"><AlertTriangle size={14} /> Dissatisfied</span>;
      default:
        return <span className="badge badge-ghost">{status}</span>;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-base-content">Submissions</h1>

      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-lg">New WhatsApp Request</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Name"
              className="input input-bordered w-full"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              required
            />
            <input
              type="tel"
              placeholder="whatsapp:+15005550006"
              className="input input-bordered w-full"
              value={formData.phone_number}
              onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
              required
            />
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? <span className="loading loading-spinner"></span> : <><Send size={18} /> Send</>}
            </button>
          </form>
          {message && (
            <div className={`alert mt-4 ${message.type === "success" ? "alert-success" : "alert-error"}`}>
              {message.text}
            </div>
          )}
        </div>
      </div>

      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="flex justify-between items-center mb-4">
            <h2 className="card-title text-lg">Recent Submissions</h2>
            <button onClick={fetchSubmissions} className="btn btn-ghost btn-sm" disabled={loading}>
              {loading ? <span className="loading loading-spinner loading-xs"></span> : <><RefreshCw size={16} /> Refresh</>}
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Submission ID</th>
                  <th>Name</th>
                  <th>Phone</th>
                  <th>Status</th>
                  <th>Message Sent</th>
                  <th>Suppression Reason</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => (
                  <tr key={sub.id}>
                    <td className="font-mono text-xs flex items-center gap-2">
                      <span className="truncate max-w-[150px]" title={sub.id}>{sub.id}</span>
                      <button 
                        className="btn btn-ghost btn-xs" 
                        onClick={() => copyToClipboard(sub.id)}
                        title="Copy ID"
                      >
                        <Copy size={14} />
                      </button>
                    </td>
                    <td className="font-medium">{sub.first_name}</td>
                    <td className="font-mono text-sm">{sub.phone_number}</td>
                    <td>{getStatusBadge(sub.status)}</td>
                    <td>{sub.sms_sent ? "Yes" : "No"}</td>
                    <td className="text-sm text-base-content/70 max-w-xs truncate">
                      {sub.suppression_reason || "-"}
                    </td>
                    <td className="text-sm">{new Date(sub.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {submissions.length === 0 && !loading && (
              <div className="text-center py-8 text-base-content/50">
                No submissions found.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}