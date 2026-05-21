import { Link } from "react-router";

export default function Navbar() {
  return (
    <div className="navbar bg-base-200 shadow-sm px-4">
      <div className="flex-1">
        <Link to="/" className="text-xl font-bold text-primary">
          PoC Template
        </Link>
      </div>
      <div className="flex-none">
        <ul className="menu menu-horizontal px-1">
          <li>
            <Link to="/">Items</Link>
          </li>
        </ul>
      </div>
    </div>
  );
}
