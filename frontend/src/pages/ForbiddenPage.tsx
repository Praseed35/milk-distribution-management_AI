import { Link } from "react-router-dom";

export default function ForbiddenPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
      <h1 className="text-6xl font-bold text-slate-300 mb-4">403</h1>
      <p className="text-lg text-slate-600 mb-6">
        You do not have permission to access this page.
      </p>
      <Link to="/" className="text-indigo-600 hover:text-indigo-800">
        Go to Dashboard
      </Link>
    </div>
  );
}
