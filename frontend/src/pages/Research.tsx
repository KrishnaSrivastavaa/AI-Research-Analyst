import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import DocumentPanel from "../components/DocumentPanel";

import {
  createConversation,
  getConversations,
  getConversationDocuments,
  getMessages,
  sendMessage,
} from "../services/api";

import type { Conversation, Document, Message } from "../types";

export default function Research() {
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[]>([]);

  // Documents attached to the currently selected conversation
  const [documents, setDocuments] = useState<Document[]>([]);

  // Currently selected conversation
  const [selectedConversation, setSelectedConversation] =
    useState<Conversation | null>(null);

  // Messages for the currently selected conversation
  const [messages, setMessages] = useState<Message[]>([]);

  const [loadingMessages, setLoadingMessages] = useState(false);

  const [loadingConversations, setLoadingConversations] = useState(true);

  const [error, setError] = useState("");

  const [showNewChatModal, setShowNewChatModal] = useState(false);

  const [newChatTitle, setNewChatTitle] = useState("");

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    try {
      setLoadingConversations(true);
      setError("");

      const conversationData = await getConversations();

      setConversations(conversationData);


      if (conversationData.length > 0) {
        await selectConversation(conversationData[0]);
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to load research workspace.",
      );
    } finally {
      setLoadingConversations(false);
    }
  }

  async function selectConversation(conversation: Conversation) {
    try {
      setSelectedConversation(conversation);

      setLoadingMessages(true);
      setMessages([]);
      setDocuments([]);

      const [messageData, documentData] = await Promise.all([
        getMessages(conversation.id),
        getConversationDocuments(conversation.id),
      ]);

      // Messages belonging to this conversation
      setMessages(messageData);

      // Documents attached to this conversation
      setDocuments(documentData);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to load conversation.",
      );
    } finally {
      setLoadingMessages(false);
    }
  }

  function openNewChatModal() {
    setNewChatTitle("");
    setError("");
    setShowNewChatModal(true);
  }

  async function handleNewConversation() {
    const trimmedTitle = newChatTitle.trim();

    if (!trimmedTitle) {
      setError("Please enter a conversation name.");
      return;
    }

    try {
      setError("");

      const conversation = await createConversation(trimmedTitle);

      setConversations((previous) => [conversation, ...previous]);

      setSelectedConversation(conversation);
      setMessages([]);
      setDocuments([]);

      setNewChatTitle("");
      setShowNewChatModal(false);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to create conversation.",
      );
    }
  }

  async function handleSendMessage(query: string) {
    if (!selectedConversation) {
      return;
    }

    try {
      setError("");

      const temporaryUserMessage: Message = {
        id: Date.now(),
        conversation_id: selectedConversation.id,
        role: "user",
        content: query,
        created_at: new Date().toISOString(),
      };

      setMessages((previous) => [...previous, temporaryUserMessage]);

      const response = await sendMessage(selectedConversation.id, query);

      const temporaryAssistantMessage: Message = {
        id: Date.now() + 1,
        conversation_id: selectedConversation.id,
        role: "assistant",
        content: response.answer,
        created_at: new Date().toISOString(),
        citations: response.citations,
      };

      setMessages((previous) => [...previous, temporaryAssistantMessage]);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to send message.",
      );
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_id");

    navigate("/auth", { replace: true });
  }

  return (
    <div className="flex h-screen bg-[#0D1220]">
      <aside className="flex h-full w-72 shrink-0 flex-col">
        {/* Sidebar */}
        <div className="min-h-0 flex-1">
          <Sidebar
            conversations={conversations}
            selectedConversationId={selectedConversation?.id ?? null}
            onSelectConversation={selectConversation}
            onNewConversation={openNewChatModal}
          />
        </div>

        {/* Documents */}
        <DocumentPanel
          documents={documents}
          conversationId={selectedConversation?.id ?? null}
          onDocumentsChange={setDocuments}
        />
      </aside>

      <ChatWindow
        conversation={selectedConversation}
        messages={messages}
        documents={documents}
        loadingMessages={loadingMessages || loadingConversations}
        onSendMessage={handleSendMessage}
        onLogout={handleLogout}
      />

      {/* NEW CHAT MODAL */}
      {showNewChatModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowNewChatModal(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl border border-white/[0.08] bg-[#111827] p-6 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-white">New Research</h2>

              <p className="mt-1 text-sm text-slate-500">
                Give your research workspace a name.
              </p>
            </div>

            <div>
              <label
                htmlFor="new-chat-title"
                className="mb-2 block text-xs font-medium uppercase tracking-wider text-slate-500"
              >
                Research name
              </label>

              <input
                id="new-chat-title"
                type="text"
                value={newChatTitle}
                onChange={(event) => setNewChatTitle(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleNewConversation();
                  }

                  if (event.key === "Escape") {
                    setShowNewChatModal(false);
                  }
                }}
                autoFocus
                placeholder="e.g. RAG Research"
                className="w-full rounded-lg border border-white/[0.08] bg-[#0D1220] px-3 py-3 text-sm text-white outline-none placeholder:text-slate-600 transition focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20"
              />
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowNewChatModal(false)}
                className="rounded-lg px-4 py-2.5 text-sm font-medium text-slate-400 transition hover:bg-white/[0.05] hover:text-white"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleNewConversation}
                disabled={!newChatTitle.trim()}
                className="rounded-lg bg-gradient-to-r from-violet-600 to-violet-500 px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-violet-900/20 transition hover:from-violet-500 hover:to-violet-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Create Research
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ERROR TOAST */}
      {error && (
        <div className="fixed bottom-4 right-4 rounded-lg border border-red-800 bg-red-950 px-4 py-3 text-sm text-red-300 shadow-lg">
          {error}
        </div>
      )}
    </div>
  );
}
