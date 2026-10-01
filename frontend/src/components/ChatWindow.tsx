import { useEffect, useRef, useState } from "react";
import type { Conversation, Message } from "../types";

import Citation from "./Citation";

interface ChatWindowProps {
  conversation: Conversation | null;
  messages: Message[];
  loadingMessages: boolean;
  onSendMessage: (query: string) => Promise<void>;
  onLogout: () => void;
  onOpenSidebar: () => void;
}

export default function ChatWindow({
  conversation,
  messages,
  loadingMessages,
  onSendMessage,
  onLogout,
  onOpenSidebar,
}: ChatWindowProps) {
  const [query, setQuery] = useState("");
  const [sending, setSending] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, sending]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || sending) {
      return;
    }

    setSending(true);

    try {
      await onSendMessage(trimmedQuery);
      setQuery("");
    } finally {
      setSending(false);
    }
  }

  if (!conversation) {
    return (
      <main className="flex min-w-0 flex-1 items-center justify-center bg-[#0D1220] px-6">
        <div className="text-center">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-500/10 ring-1 ring-violet-500/20">
            <span className="text-2xl">✦</span>
          </div>

          <h2 className="text-2xl font-semibold tracking-tight text-slate-100">
            AI Research Analyst
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Create a conversation to start researching.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-w-0 flex-1 flex-col bg-[#0D1220]">
      {/* Header */}

      <header className="flex shrink-0 items-center justify-between border-b border-white/[0.06] bg-[#0D1220]/95 px-3 py-3 backdrop-blur sm:px-6 sm:py-4">
        <div className="flex min-w-0 items-center gap-3">
          {/* Mobile menu button */}
          <button
            type="button"
            onClick={onOpenSidebar}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-white/[0.05] hover:text-white md:hidden"
            aria-label="Open sidebar"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="h-5 w-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold tracking-tight text-slate-100 sm:text-base">
              {conversation.title}
            </h2>

            <p className="mt-0.5 text-[11px] text-slate-500 sm:text-xs">
              Research workspace
            </p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-5">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]" />

            <span className="hidden text-xs text-slate-500 sm:inline">
              Ready
            </span>
          </div>

          {/* Desktop logout */}
          <button
            type="button"
            onClick={onLogout}
            className="hidden items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium text-slate-500 transition hover:bg-red-500/[0.06] hover:text-red-400 md:flex"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="h-4 w-4"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6A2.25 2.25 0 0 0 5.25 5.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M18 12H9m0 0 3-3m-3 3 3 3"
              />
            </svg>
            Logout
          </button>
        </div>
      </header>

      {/* Messages */}

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5 sm:px-6 sm:py-8">
        {loadingMessages ? (
          <div className="flex h-full items-center justify-center">
            <div className="flex items-center gap-3 text-sm text-slate-500">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-700 border-t-violet-400" />
              Loading conversation...
            </div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-md px-4 text-center">
              <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500/15 to-cyan-500/10 ring-1 ring-white/[0.06]">
                <span className="text-xl text-violet-300">✦</span>
              </div>

              <h3 className="text-xl font-semibold text-slate-100">
                Start your research
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Ask a question about the documents connected to this
                conversation.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-4xl space-y-6 sm:space-y-7">
            {messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.role === "user"
                    ? "flex justify-end"
                    : "flex justify-start"
                }
              >
                <div
                  className={
                    message.role === "user"
                      ? "max-w-[90%] rounded-2xl rounded-br-md bg-gradient-to-br from-violet-600 to-violet-700 px-4 py-3 text-white shadow-lg shadow-violet-950/20 sm:max-w-[75%] sm:px-5 sm:py-3.5"
                      : "max-w-[92%] rounded-2xl rounded-bl-md border border-white/[0.06] bg-[#171E2E] px-4 py-3.5 text-slate-200 shadow-lg shadow-black/10 sm:max-w-[78%] sm:px-5 sm:py-4"
                  }
                >
                  <div
                    className={
                      message.role === "user"
                        ? "mb-1.5 text-[11px] font-medium text-violet-200"
                        : "mb-1.5 text-[11px] font-medium text-cyan-400"
                    }
                  >
                    {message.role === "user" ? "You" : "Research Analyst"}
                  </div>

                  <div className="whitespace-pre-wrap break-words text-sm leading-6 sm:leading-7">
                    {message.content}
                  </div>

                  {message.role === "assistant" &&
                    message.citations &&
                    message.citations.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
                          Sources
                        </p>

                        <div className="space-y-1.5">
                          {message.citations.map((citation) => (
                            <Citation
                              key={`${message.id}-${citation.id}`}
                              citation={citation}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            ))}

            {/* AI thinking indicator */}

            {sending && (
              <div className="flex justify-start">
                <div className="max-w-[92%] rounded-2xl rounded-bl-md border border-white/[0.06] bg-[#171E2E] px-4 py-3.5 shadow-lg shadow-black/10 sm:max-w-[78%] sm:px-5 sm:py-4">
                  <div className="mb-2 text-[11px] font-medium text-cyan-400">
                    Research Analyst
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:-0.3s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-violet-400 [animation-delay:-0.15s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-400" />
                    </div>

                    <span className="ml-1 text-xs text-slate-500">
                      Researching your documents...
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}

      <div className="shrink-0 border-t border-white/[0.06] bg-[#0B0F1A] px-3 py-3 sm:h-[96px] sm:px-4 sm:py-3">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-4xl items-center gap-2 sm:gap-3"
        >
          <div className="relative min-w-0 flex-1">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              disabled={sending}
              placeholder={
                sending
                  ? "Researching..."
                  : "Ask a question about your documents..."
              }
              className="w-full rounded-xl border border-white/[0.08] bg-[#151B2A] px-3 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-60 sm:px-4 sm:py-3.5"
            />
          </div>

          <button
            type="submit"
            disabled={sending || !query.trim()}
            className="flex h-11 min-w-[68px] shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-4 text-sm font-semibold text-white shadow-lg shadow-violet-950/30 transition hover:from-violet-500 hover:to-violet-400 disabled:cursor-not-allowed disabled:opacity-40 sm:h-12 sm:min-w-[82px] sm:px-5"
          >
            {sending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            ) : (
              "Send"
            )}
          </button>
        </form>

        <p className="mx-auto mt-1 hidden max-w-4xl px-1 text-[11px] text-slate-600 sm:block">
          Answers are generated from your selected research documents.
        </p>
      </div>
    </main>
  );
}
