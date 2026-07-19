import { createBrowserRouter, useRouteError, useNavigate } from "react-router";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

function ErrorBoundary() {
  const error: any = useRouteError();
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#08080e] text-white flex flex-col items-center justify-center p-4 font-['Inter']">
      <div className="max-w-md w-full bg-white/[0.02] border border-white/10 rounded-2xl p-8 text-center">
        <div className="w-16 h-16 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        </div>
        <h1 className="text-2xl font-bold mb-3">Oops! Something went wrong.</h1>
        <p className="text-gray-400 text-sm mb-8">
          {error?.statusText || error?.message || 'An unexpected error occurred.'}
        </p>
        <button
          onClick={() => navigate('/')}
          className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-all"
        >
          Return to Home
        </button>
      </div>
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Home,
    errorElement: <ErrorBoundary />,
  },
  {
    path: "/dashboard",
    Component: Dashboard,
    errorElement: <ErrorBoundary />,
  },
]);
