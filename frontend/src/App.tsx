import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "@/layouts/MainLayout";
import SubmissionPage from "@/pages/submissions/SubmissionPage";
import FeedbackPage from "@/pages/feedback/FeedbackPage";
import ReviewReplyPage from "@/pages/review-replies/ReviewReplyPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<SubmissionPage />} />
          <Route path="feedback" element={<FeedbackPage />} />
          <Route path="review-replies" element={<ReviewReplyPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}