import { Outlet, Link, useLocation } from "react-router-dom";
import { Menu } from "lucide-react";

export default function MainLayout() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const getLinkClass = (path: string) =>
    `link link-hover text-base ${isActive(path) ? "link-primary font-semibold" : ""}`;

  return (
    <div className="min-h-screen bg-base-200 flex flex-col">
      <header className="navbar bg-base-100 shadow-sm sticky top-0 z-50 px-4 lg:px-8">
        <div className="navbar-start">
          <Link to="/" className="text-xl font-bold text-primary">
            Google Review Workflow PoC
          </Link>
        </div>
        <div className="navbar-center hidden lg:flex">
          <ul className="menu menu-horizontal px-1 gap-4">
            <li><Link to="/" className={getLinkClass("/")}>Submissions</Link></li>
            <li><Link to="/feedback" className={getLinkClass("/feedback")}>Feedback</Link></li>
            <li><Link to="/review-replies" className={getLinkClass("/review-replies")}>AI Replies</Link></li>
          </ul>
        </div>
        <div className="navbar-end">
          <div className="dropdown dropdown-end">
            <div tabIndex={0} role="button" className="btn btn-ghost btn-circle lg:hidden">
              <Menu size={20} />
            </div>
            <ul tabIndex={0} className="dropdown-content menu p-2 shadow-lg bg-base-100 rounded-box w-52 mt-3">
              <li><Link to="/">Submissions</Link></li>
              <li><Link to="/feedback">Feedback</Link></li>
              <li><Link to="/review-replies">AI Replies</Link></li>
            </ul>
          </div>
        </div>
      </header>

      <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}