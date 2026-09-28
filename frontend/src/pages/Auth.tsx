import { useState } from "react";
import { useNavigate } from "react-router-dom"
import { signin, signup } from "../services/api";

type AuthMode = "signin" | "signup";

export default function Auth() {
    const navigate = useNavigate();
    const [mode, setMode] = useState<AuthMode>("signin");

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleSubmit = async (
        event: React.SubmitEvent<HTMLFormElement>
    ) => {
        event.preventDefault();

        setError("");
        setSuccess("");
        setLoading(true);

        try {
            if (mode === "signup") {
                const data = await signup(email, password);

                setSuccess(data.message);

                setMode("signin");
                setPassword("");
            } else {
                const data = await signin(email, password);

                localStorage.setItem(
                    "access_token",
                    data.access_token
                );

                localStorage.setItem(
                    "refresh_token",
                    data.refresh_token
                );

                localStorage.setItem(
                    "user_id",
                    data.user_id
                );

                navigate("/research");

                // We'll redirect to /research next.
            }
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Something went wrong."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
            <div className="w-full max-w-md rounded-2xl bg-gray-900 p-8 shadow-xl">

                {/* Header */}

                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold text-white">
                        AI Research Analyst
                    </h1>

                    <p className="mt-2 text-gray-400">
                        Research your documents with AI
                    </p>
                </div>


                {/* Auth mode selector */}

                <div className="mb-6 flex rounded-lg bg-gray-800 p-1">

                    <button
                        type="button"
                        onClick={() => {
                            setMode("signin");
                            setError("");
                            setSuccess("");
                        }}
                        className={`flex-1 rounded-md py-2 text-sm font-medium ${
                            mode === "signin"
                                ? "bg-white text-gray-900"
                                : "text-gray-400 hover:text-white"
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
                        className={`flex-1 rounded-md py-2 text-sm font-medium ${
                            mode === "signup"
                                ? "bg-white text-gray-900"
                                : "text-gray-400 hover:text-white"
                        }`}
                    >
                        Sign Up
                    </button>

                </div>


                {/* Form */}

                <form
                    onSubmit={handleSubmit}
                    className="space-y-5"
                >

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
                            onChange={(event) =>
                                setEmail(event.target.value)
                            }
                            required
                            autoComplete="email"
                            placeholder="you@example.com"
                            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
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
                            onChange={(event) =>
                                setPassword(event.target.value)
                            }
                            required
                            autoComplete={
                                mode === "signin"
                                    ? "current-password"
                                    : "new-password"
                            }
                            placeholder="••••••••"
                            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none transition focus:border-blue-500"
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
                        <div className="rounded-lg border border-green-800 bg-green-950/50 px-4 py-3 text-sm text-green-400">
                            {success}
                        </div>
                    )}


                    {/* Submit */}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
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
                            setMode(
                                mode === "signin"
                                    ? "signup"
                                    : "signin"
                            );

                            setError("");
                            setSuccess("");
                        }}
                        className="font-medium text-blue-400 hover:text-blue-300"
                    >
                        {mode === "signin"
                            ? "Create one"
                            : "Sign in"}
                    </button>
                </p>

            </div>
        </div>
    );
}