import type { Conversation } from "../types";

interface SidebarProps {
    conversations: Conversation[];
    selectedConversationId: number | null;
    onSelectConversation: (conversation: Conversation) => void;
    onNewConversation: () => void;
}

export default function Sidebar({
    conversations,
    selectedConversationId,
    onSelectConversation,
    onNewConversation,
}: SidebarProps) {
    return (
        <div className="flex h-full flex-col border-r border-white/[0.06]">

            {/* Brand */}

            <div className="border-b border-white/[0.06] p-5">

                <div className="flex items-center gap-3">

                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 shadow-lg shadow-violet-950/30">
                        <span className="text-lg font-bold text-white">
                            ✦
                        </span>
                    </div>

                    <div>
                        <h1 className="text-sm font-semibold text-slate-100">
                            AI Research Analyst
                        </h1>

                        <p className="text-[11px] text-slate-500">
                            Research workspace
                        </p>
                    </div>

                </div>


                <button
                    onClick={onNewConversation}
                    className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-950/20 transition hover:from-violet-500 hover:to-violet-400"
                >
                    <span className="text-lg leading-none">
                        +
                    </span>

                    New Chat
                </button>

            </div>


            {/* Conversations */}

            <div className="flex-1 overflow-y-auto p-3">

                <div className="mb-3 px-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
                    Conversations
                </div>

                <div className="space-y-1">

                    {conversations.map((conversation) => (
                        <button
                            key={conversation.id}
                            onClick={() =>
                                onSelectConversation(conversation)
                            }
                            className={`group w-full rounded-xl px-3 py-3 text-left text-sm transition ${
                                selectedConversationId ===
                                conversation.id
                                    ? "bg-[#1B2438] text-slate-100 shadow-sm ring-1 ring-white/[0.04]"
                                    : "text-slate-500 hover:bg-white/[0.03] hover:text-slate-300"
                            }`}
                        >

                            <div className="flex items-center gap-2">

                                <span
                                    className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                                        selectedConversationId ===
                                        conversation.id
                                            ? "bg-cyan-400 shadow-[0_0_7px_rgba(34,211,238,0.7)]"
                                            : "bg-slate-700"
                                    }`}
                                />

                                <span className="truncate">
                                    {conversation.title}
                                </span>

                            </div>

                        </button>
                    ))}

                </div>


                {conversations.length === 0 && (
                    <div className="px-3 py-8 text-center">
                        <p className="text-xs text-slate-600">
                            No conversations yet
                        </p>

                        <p className="mt-1 text-[11px] text-slate-700">
                            Start a new research chat
                        </p>
                    </div>
                )}

            </div>


            {/* Bottom */}

            <div className="border-t border-white/[0.06] p-4">

                <div className="flex items-center gap-2 text-xs text-slate-600">
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    Backend connected
                </div>

            </div>

        </div>
    );
}