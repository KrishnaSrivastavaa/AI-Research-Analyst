import type { Conversation } from "../types";

interface SidebarProps {
  conversations: Conversation[];
  selectedConversationId: number | null;
  onSelectConversation: (conversation: Conversation) => void;
  onNewConversation: () => void;
  onLogout: () => void;
  onCloseMobile: () => void;
}

export default function Sidebar({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onNewConversation,
  onLogout,
  onCloseMobile,
}: SidebarProps) {
  return (
    <div className="flex h-full min-h-0 flex-col border-r border-white/[0.06]">
      {/* Brand */}

      <div className="border-b border-white/[0.06] p-4 sm:p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-950/30">
              <span className="text-lg font-bold text-white">✦</span>
            </div>

            <div className="min-w-0">
              <h1 className="truncate text-sm font-semibold text-slate-100">
                AI Research Analyst
              </h1>

              <p className="text-[11px] text-slate-500">
                Research workspace
              </p>
            </div>
          </div>

          {/* Mobile close button */}
          <button
            type="button"
            onClick={onCloseMobile}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition hover:bg-white/[0.05] hover:text-white md:hidden"
            aria-label="Close sidebar"
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
                d="M6 6l12 12M18 6L6 18"
              />
            </svg>
          </button>
        </div>

        <button
          onClick={onNewConversation}
          className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-950/20 transition hover:from-violet-500 hover:to-violet-400"
        >
          <span className="text-lg leading-none">+</span>
          New Chat
        </button>
      </div>

      {/* Conversations */}

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        <div className="mb-3 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
          Conversations
        </div>

        <div className="space-y-1">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => onSelectConversation(conversation)}
              className={`group w-full rounded-xl px-3 py-3 text-left text-sm transition ${
                selectedConversationId === conversation.id
                  ? "bg-[#1B2438] text-slate-100 shadow-sm ring-1 ring-white/[0.04]"
                  : "text-slate-500 hover:bg-white/[0.03] hover:text-slate-300"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                    selectedConversationId === conversation.id
                      ? "bg-cyan-400 shadow-[0_0_7px_rgba(34,211,238,0.7)]"
                      : "bg-slate-700"
                  }`}
                />

                <span className="truncate">{conversation.title}</span>
              </div>
            </button>
          ))}
        </div>

        {conversations.length === 0 && (
          <div className="px-3 py-8 text-center">
            <p className="text-xs text-slate-600">No conversations yet</p>

            <p className="mt-1 text-[11px] text-slate-700">
              Start a new research chat
            </p>
          </div>
        )}
      </div>

      {/* Bottom */}

      <div className="border-t border-white/[0.06] p-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span className="h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
            Backend connected
          </div>

          {/* Logout only appears here on mobile */}
          <button
            type="button"
            onClick={onLogout}
            className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-slate-500 transition hover:bg-red-500/[0.06] hover:text-red-400 md:hidden"
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
      </div>
    </div>
  );
}