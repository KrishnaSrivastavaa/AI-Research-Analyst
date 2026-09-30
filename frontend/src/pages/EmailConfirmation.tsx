import { useNavigate } from "react-router-dom";

export default function EmailConfirmation() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-950 px-4">
      <div className="w-full max-w-md rounded-2xl bg-gray-900 p-8 text-center shadow-xl">
        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              className="h-6 w-6 text-white"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m5 12 4 4L19 7"
              />
            </svg>
          </div>
        </div>

        <h1 className="text-2xl font-bold text-white">Email Verified</h1>

        <p className="mt-3 text-gray-400">
          Your email has been successfully verified. You can now sign in to your
          account.
        </p>

        <button
          type="button"
          onClick={() => navigate("/auth")}
          className="mt-6 w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-500"
        >
          Continue to Sign In
        </button>
      </div>
    </div>
  );
}
