import { useState, useEffect } from "react";
import { Wand2, RefreshCw, Star, ThumbsUp, ThumbsDown, Copy } from "lucide-react";

const API_KEY = import.meta.env.VITE_API_KEY || "";
const BASE_URL = "/api";

type ReviewReply = {
  id: string;
  customer_name: string;
  star_rating: number;
  review_text: string;
  generated_reply: string;
  moderation_status: "auto-approved" | "requires-approval";
  created_at: string;
};

export default function ReviewReplyPage() {
  const [replies, setReplies] = useState<ReviewReply[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    customer_name: "",
    star_rating: 5,
    review_text: "",
  });
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchReplies = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/review-replies`, {
        headers: { "X-API-Key": API_KEY },
      });
      if (!res.ok) throw new Error("Failed to fetch replies");
      const data = await res.json();
      setReplies(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReplies();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const res = await fetch(`${BASE_URL}/review-replies/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Request failed");
      
      // Fix: Backend returns the object directly, not wrapped in a "reply" key
      const newReply = data;
      
      setMessage({ type: "success", text: `Reply generated. Status: ${newReply.moderation_status}` });
      setFormData({ customer_name: "", star_rating: 5, review_text: "" });
      fetchReplies();
    } catch (err: any) {
      setMessage({ type: "error", text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "auto-approved":
        return <span className="badge badge-success gap-2"><ThumbsUp size={14} /> Auto Approved</span>;
      case "requires-approval":
        return <span className="badge badge-warning gap-2"><ThumbsDown size={14} /> Needs Approval</span>;
      default:
        return <span className="badge badge-ghost">{status}</span>;
    }
  };

  const renderStars = (count: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        size={14}
        className={i < count ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}
      />
    ));
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-base-content">AI Review Replies</h1>

      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <h2 className="card-title text-lg">Generate Reply</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-control w-full">
                <label className="label"><span className="label-text">Customer Name</span></label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  className="input input-bordered w-full"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  required
                />
              </div>
              <div className="form-control w-full">
                <label className="label"><span className="label-text">Star Rating</span></label>
                <select
                  className="select select-bordered w-full"
                  value={formData.star_rating}
                  onChange={(e) => setFormData({ ...formData, star_rating: Number(e.target.value) })}
                >
                  {[1, 2, 3, 4, 5].map((r) => (
                    <option key={r} value={r}>{r} Star{r > 1 ? "s" : ""}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-control w-full">
              <label className="label"><span className="label-text">Original Review Text</span></label>
              <textarea
                className="textarea textarea-bordered h-24"
                placeholder="Paste the customer's review here..."
                value={formData.review_text}
                onChange={(e) => setFormData({ ...formData, review_text: e.target.value })}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? <span className="loading loading-spinner"></span> : <><Wand2 size={18} /> Generate Reply</>}
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
            <h2 className="card-title text-lg">Generated Replies History</h2>
            <button onClick={fetchReplies} className="btn btn-ghost btn-sm" disabled={loading}>
              {loading ? <span className="loading loading-spinner loading-xs"></span> : <><RefreshCw size={16} /> Refresh</>}
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Rating</th>
                  <th>Original Review</th>
                  <th>Generated Reply</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {replies.map((rep) => (
                  <tr key={rep.id}>
                    <td className="font-medium">{rep.customer_name}</td>
                    <td>
                      <div className="flex">{renderStars(rep.star_rating)}</div>
                    </td>
                    <td className="text-sm max-w-xs truncate" title={rep.review_text}>
                      {rep.review_text}
                    </td>
                    <td className="text-sm max-w-sm truncate" title={rep.generated_reply}>
                      {rep.generated_reply}
                    </td>
                    <td>
                      {rep.moderation_status ? getStatusBadge(rep.moderation_status) : <span className="badge badge-ghost">Pending</span>}
                    </td>
                    <td>
                      <button 
                        className="btn btn-ghost btn-xs" 
                        onClick={() => copyToClipboard(rep.generated_reply)}
                        title="Copy Reply"
                      >
                        <Copy size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {replies.length === 0 && !loading && (
              <div className="text-center py-8 text-base-content/50">
                No replies generated yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// import { useState, useEffect } from "react";
// import { Wand2, RefreshCw, Star, ThumbsUp, ThumbsDown, Copy } from "lucide-react";

// const API_KEY = import.meta.env.VITE_API_KEY || "";
// const BASE_URL = "/api";

// type ReviewReply = {
//   id: string;
//   customer_name: string;
//   star_rating: number;
//   review_text: string;
//   generated_reply: string;
//   moderation_status: "auto-approved" | "requires-approval";
//   created_at: string;
// };

// export default function ReviewReplyPage() {
//   const [replies, setReplies] = useState<ReviewReply[]>([]);
//   const [loading, setLoading] = useState(false);
//   const [submitting, setSubmitting] = useState(false);
//   const [formData, setFormData] = useState({
//     customer_name: "",
//     star_rating: 5,
//     review_text: "",
//   });
//   const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

//   const fetchReplies = async () => {
//     setLoading(true);
//     try {
//       const res = await fetch(`${BASE_URL}/review-replies`, {
//         headers: { "X-API-Key": API_KEY },
//       });
//       if (!res.ok) throw new Error("Failed to fetch replies");
//       const data = await res.json();
//       setReplies(Array.isArray(data) ? data : []);
//     } catch (err) {
//       console.error(err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchReplies();
//   }, []);

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     setSubmitting(true);
//     setMessage(null);
//     try {
//       const res = await fetch(`${BASE_URL}/review-replies/generate`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
//         body: JSON.stringify(formData),
//       });
//       const data = await res.json();
//       if (!res.ok) throw new Error(data.detail || data.message || "Request failed");
      
//       const newReply = data.reply;
      
//       setMessage({ type: "success", text: `Reply generated. Status: ${newReply.moderation_status}` });
//       setFormData({ customer_name: "", star_rating: 5, review_text: "" });
//       fetchReplies();
//     } catch (err: any) {
//       setMessage({ type: "error", text: err.message });
//     } finally {
//       setSubmitting(false);
//     }
//   };

//   const copyToClipboard = (text: string) => {
//     navigator.clipboard.writeText(text);
//   };

//   const getStatusBadge = (status: string) => {
//     switch (status) {
//       case "auto-approved":
//         return <span className="badge badge-success gap-2"><ThumbsUp size={14} /> Auto Approved</span>;
//       case "requires-approval":
//         return <span className="badge badge-warning gap-2"><ThumbsDown size={14} /> Needs Approval</span>;
//       default:
//         return <span className="badge badge-ghost">{status}</span>;
//     }
//   };

//   const renderStars = (count: number) => {
//     return Array.from({ length: 5 }).map((_, i) => (
//       <Star
//         key={i}
//         size={14}
//         className={i < count ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}
//       />
//     ));
//   };

//   return (
//     <div className="space-y-6">
//       <h1 className="text-3xl font-bold text-base-content">AI Review Replies</h1>

//       <div className="card bg-base-100 shadow-xl">
//         <div className="card-body">
//           <h2 className="card-title text-lg">Generate Reply</h2>
//           <form onSubmit={handleSubmit} className="space-y-4">
//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               <div className="form-control w-full">
//                 <label className="label"><span className="label-text">Customer Name</span></label>
//                 <input
//                   type="text"
//                   placeholder="e.g. John Doe"
//                   className="input input-bordered w-full"
//                   value={formData.customer_name}
//                   onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
//                   required
//                 />
//               </div>
//               <div className="form-control w-full">
//                 <label className="label"><span className="label-text">Star Rating</span></label>
//                 <select
//                   className="select select-bordered w-full"
//                   value={formData.star_rating}
//                   onChange={(e) => setFormData({ ...formData, star_rating: Number(e.target.value) })}
//                 >
//                   {[1, 2, 3, 4, 5].map((r) => (
//                     <option key={r} value={r}>{r} Star{r > 1 ? "s" : ""}</option>
//                   ))}
//                 </select>
//               </div>
//             </div>
//             <div className="form-control w-full">
//               <label className="label"><span className="label-text">Original Review Text</span></label>
//               <textarea
//                 className="textarea textarea-bordered h-24"
//                 placeholder="Paste the customer's review here..."
//                 value={formData.review_text}
//                 onChange={(e) => setFormData({ ...formData, review_text: e.target.value })}
//                 required
//               />
//             </div>
//             <button type="submit" className="btn btn-primary" disabled={submitting}>
//               {submitting ? <span className="loading loading-spinner"></span> : <><Wand2 size={18} /> Generate Reply</>}
//             </button>
//           </form>
//           {message && (
//             <div className={`alert mt-4 ${message.type === "success" ? "alert-success" : "alert-error"}`}>
//               {message.text}
//             </div>
//           )}
//         </div>
//       </div>

//       <div className="card bg-base-100 shadow-xl">
//         <div className="card-body">
//           <div className="flex justify-between items-center mb-4">
//             <h2 className="card-title text-lg">Generated Replies History</h2>
//             <button onClick={fetchReplies} className="btn btn-ghost btn-sm" disabled={loading}>
//               {loading ? <span className="loading loading-spinner loading-xs"></span> : <><RefreshCw size={16} /> Refresh</>}
//             </button>
//           </div>
//           <div className="overflow-x-auto">
//             <table className="table table-zebra">
//               <thead>
//                 <tr>
//                   <th>Customer</th>
//                   <th>Rating</th>
//                   <th>Original Review</th>
//                   <th>Generated Reply</th>
//                   <th>Status</th>
//                   <th>Actions</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {replies.map((rep) => (
//                   <tr key={rep.id}>
//                     <td className="font-medium">{rep.customer_name}</td>
//                     <td>
//                       <div className="flex">{renderStars(rep.star_rating)}</div>
//                     </td>
//                     <td className="text-sm max-w-xs truncate" title={rep.review_text}>
//                       {rep.review_text}
//                     </td>
//                     <td className="text-sm max-w-sm truncate" title={rep.generated_reply}>
//                       {rep.generated_reply}
//                     </td>
//                     <td>{getStatusBadge(rep.moderation_status)}</td>
//                     <td>
//                       <button 
//                         className="btn btn-ghost btn-xs" 
//                         onClick={() => copyToClipboard(rep.generated_reply)}
//                         title="Copy Reply"
//                       >
//                         <Copy size={14} />
//                       </button>
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//             {replies.length === 0 && !loading && (
//               <div className="text-center py-8 text-base-content/50">
//                 No replies generated yet.
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }