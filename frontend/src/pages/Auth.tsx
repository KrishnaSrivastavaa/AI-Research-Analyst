import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { signin, signup } from "../services/api";

type AuthMode = "signin" | "signup";

export default function Auth() {
  const navigate = useNavigate();

  const [mode, setMode] = useState<AuthMode>("signin");

  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      if (mode === "signup") {
        const data = await signup(name, email, username, password);

        setSuccess(
          data.email_confirmation_required
            ? "Account created successfully. Please check your email and click the confirmation link before signing in."
            : data.message,
        );

        setMode("signin");

        setName("");
        setUsername("");
        setPassword("");
      } else {
        const data = await signin(email, password);

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        localStorage.setItem("user_id", data.user_id);

        navigate("/research");
      }
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0D1220] px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/[0.06] bg-[#111827] p-8 shadow-2xl shadow-black/20">
        {/* Header */}

        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            AI Research Analyst
          </h1>

          <p className="mt-2 text-gray-400">
            Research your documents with AI
          </p>
        </div>

        {/* Auth mode selector */}

        <div className="mb-6 flex rounded-lg bg-[#1B2438] p-1">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setError("");
              setSuccess("");
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
              mode === "signin"
                ? "bg-gradient-to-r from-violet-600 to-violet-500 text-white shadow-lg shadow-violet-950/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>

          <button
            type="button"
            onClick={() => {
              setMode("signup");
              setError("");
              setSuccess("");
            }}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
              mode === "signup"
                ? "bg-gradient-to-r from-violet-600 to-violet-500 text-white shadow-lg shadow-violet-950/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name - Signup only */}

          {mode === "signup" && (
            <div>
              <label
                htmlFor="name"
                className="mb-2 block text-sm font-medium text-gray-300"
              >
                Name
              </label>

              <input
                id="name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                autoComplete="name"
                placeholder="Your name"
                className="w-full rounded-lg border border-white/[0.08] bg-[#1B2438] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20"
              />
            </div>
          )}

          {/* Username - Signup only */}

          {mode === "signup" && (
            <div>
              <label
                htmlFor="username"
                className="mb-2 block text-sm font-medium text-gray-300"
              >
                Username
              </label>

              <input
                id="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
                autoComplete="username"
                placeholder="Choose a username"
                className="w-full rounded-lg border border-white/[0.08] bg-[#1B2438] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20"
              />
            </div>
          )}

          {/* Email */}

          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
              placeholder="you@example.com"
              className="w-full rounded-lg border border-white/[0.08] bg-[#1B2438] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20"
            />
          </div>

          {/* Password */}

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete={
                mode === "signin" ? "current-password" : "new-password"
              }
              placeholder="••••••••"
              className="w-full rounded-lg border border-white/[0.08] bg-[#1B2438] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20"
            />
          </div>

          {/* Error */}

          {error && (
            <div className="rounded-lg border border-red-800 bg-red-950/50 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* Success */}

          {success && (
            <div className="rounded-lg border border-green-800 bg-green-950/50 px-4 py-3 text-sm leading-5 text-green-400">
              {success}
            </div>
          )}

          {/* Submit */}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-gradient-to-r from-violet-600 to-violet-500 py-3 font-semibold text-white shadow-lg shadow-violet-950/20 transition hover:from-violet-500 hover:to-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Please wait..."
              : mode === "signin"
                ? "Sign In"
                : "Create Account"}
          </button>
        </form>

        {/* Bottom text */}

        <p className="mt-6 text-center text-sm text-gray-500">
          {mode === "signin"
            ? "Don't have an account? "
            : "Already have an account? "}

          <button
            type="button"
            onClick={() => {
              setMode(mode === "signin" ? "signup" : "signin");

              setError("");
              setSuccess("");
            }}
            className="font-medium text-cyan-400 transition hover:text-cyan-300"
          >
            {mode === "signin" ? "Create one" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}