import { useState, useEffect } from "react";
import { Send, RefreshCw, ThumbsUp, ThumbsDown } from "lucide-react";

const API_KEY = import.meta.env.VITE_API_KEY || "";
const BASE_URL = "/api";

type FeedbackRecord = {
  id: string;
  submission_id: string;
  satisfaction: "yes" | "no";
  private_feedback: string | null;
  alert_email_sent: boolean;
  created_at: string;
};

export default function FeedbackPage() {
  const [feedbacks, setFeedbacks] = useState<FeedbackRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    submission_id: "",
    satisfaction: "yes" as "yes" | "no",
    private_feedback: "",
  });
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchFeedbacks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/feedback`, {
        headers: { "X-API-Key": API_KEY },
      });
      if (!res.ok) throw new Error("Failed to fetch feedback");
      const data = await res.json();
      setFeedbacks(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
      setMessage({ type: "error", text: "Failed to load feedback records" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbacks();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const res = await fetch(`${BASE_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
        body: JSON.stringify({
          ...formData,
          private_feedback: formData.private_feedback || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Request failed");
      setMessage({ type: "success", text: "Feedback recorded successfully" });
      setFormData({ submission_id: "", satisfaction: "yes", private_feedback: "" });
      fetchFeedbacks();
    } catch (err: any) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-base-content">Feedback</h1>

      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-lg">Record Customer Feedback</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-control w-full">
                <label className="label"><span className="label-text">Submission ID</span></label>
                <input
                  type="text"
                  placeholder="UUID from submissions"
                  className="input input-bordered w-full"
                  value={formData.submission_id}
                  onChange={(e) => setFormData({ ...formData, submission_id: e.target.value })}
                  required
                />
              </div>
              <div className="form-control w-full">
                <label className="label"><span className="label-text">Satisfaction</span></label>
                <select
                  className="select select-bordered w-full"
                  value={formData.satisfaction}
                  onChange={(e) => setFormData({ ...formData, satisfaction: e.target.value as "yes" | "no" })}
                >
                  <option value="yes">Yes (Satisfied)</option>
                  <option value="no">No (Dissatisfied)</option>
                </select>
              </div>
            </div>
            <div className="form-control w-full">
              <label className="label"><span className="label-text">Private Feedback (Optional)</span></label>
              <textarea
                className="textarea textarea-bordered h-24"
                placeholder="Customer comments..."
                value={formData.private_feedback}
                onChange={(e) => setFormData({ ...formData, private_feedback: e.target.value })}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? <span className="loading loading-spinner"></span> : <><Send size={18} /> Submit Feedback</>}
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
            <h2 className="card-title text-lg">Recent Feedback</h2>
            <button onClick={fetchFeedbacks} className="btn btn-ghost btn-sm" disabled={loading}>
              {loading ? <span className="loading loading-spinner loading-xs"></span> : <><RefreshCw size={16} /> Refresh</>}
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Submission ID</th>
                  <th>Satisfaction</th>
                  <th>Private Feedback</th>
                  <th>Email Alert Sent</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {feedbacks.map((fb) => (
                  <tr key={fb.id}>
                    <td className="font-mono text-xs">{fb.submission_id.slice(0, 8)}...</td>
                    <td>
                      <span className={`badge gap-1 ${fb.satisfaction === "yes" ? "badge-success" : "badge-error"}`}>
                        {fb.satisfaction === "yes" ? <ThumbsUp size={14} /> : <ThumbsDown size={14} />}
                        {fb.satisfaction === "yes" ? " Yes" : " No"}
                      </span>
                    </td>
                    <td className="max-w-xs truncate text-sm">{fb.private_feedback || "-"}</td>
                    <td>{fb.alert_email_sent ? "Yes" : "No"}</td>
                    <td className="text-sm">{new Date(fb.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {feedbacks.length === 0 && !loading && (
              <div className="text-center py-8 text-base-content/50">
                No feedback records found.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}