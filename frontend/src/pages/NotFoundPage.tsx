import { Home, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-9xl font-black text-base-300">404</h1>
      <h2 className="text-3xl font-bold text-base-content mt-4">Page Not Found</h2>
      <p className="text-base-content/60 max-w-md mt-2">
        The page you are looking for does not exist or has been moved.
      </p>
      <div className="flex gap-4 mt-8">
        <Link to="/" className="btn btn-primary">
          <Home size={18} />
          Go Home
        </Link>
        <button onClick={() => window.history.back()} className="btn btn-outline">
          <ArrowLeft size={18} />
          Go Back
        </button>
      </div>
    </div>
  );
}