import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";

import type { Document } from "../types";

import {
    uploadDocument,
    addDocumentToConversation,
    getConversationDocuments,
} from "../services/api";

interface DocumentPanelProps {
    documents: Document[];
    conversationId: number | null;

    onDocumentsChange: (
        documents: Document[]
    ) => void;

}

export default function DocumentPanel({
    documents,
    conversationId,
    onDocumentsChange,
}: DocumentPanelProps) {
    const fileInputRef =
        useRef<HTMLInputElement>(null);

    const currentConversationIdRef =
        useRef<number | null>(conversationId);

    useEffect(() => {
        currentConversationIdRef.current =
            conversationId;
    }, [conversationId]);

    const [uploading, setUploading] =
        useState(false);

    const [error, setError] =
        useState("");

    async function handleFileChange(
        event: ChangeEvent<HTMLInputElement>
    ) {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        if (!conversationId) {
            setError(
                "Please select a conversation first."
            );
            return;
        }

        if (file.type !== "application/pdf") {
            setError(
                "Only PDF files are supported."
            );
            return;
        }

        // Conversation where the upload started.
        const uploadConversationId =
            conversationId;

        try {
            setError("");
            setUploading(true);

            /*
             * Step 1:
             * Upload the document and create the
             * document record + Qdrant embeddings.
             */
            const uploadResponse =
                await uploadDocument(file);

            const documentId =
                uploadResponse.document.id;

            /*
             * Step 2:
             * Attach the document to the
             * conversation where the upload started.
             */
            await addDocumentToConversation(
                uploadConversationId,
                documentId
            );

            /*
             * Step 3:
             * Refresh the documents for the
             * conversation where the upload started.
             */
            const conversationDocuments =
                await getConversationDocuments(
                    uploadConversationId
                );

            /*
             * Only update the currently displayed
             * conversation if the user is still on
             * the conversation where the upload started.
             */
            if (
                currentConversationIdRef.current ===
                uploadConversationId
            ) {
                onDocumentsChange(
                    conversationDocuments
                );
            }

            /*
             * Step 4:
             * Refresh the user's complete document
             * library regardless of the currently
             * selected conversation.
             */

            
        } catch (error) {
            setError(
                error instanceof Error
                    ? error.message
                    : "Failed to upload document."
            );
        } finally {
            setUploading(false);

            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    }

    return (
        <div className="shrink-0 border-t border-white/[0.06] p-3">

            {/* Header */}

            <div className="mb-2 flex items-center justify-between">

                <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-600">
                    Documents
                </span>

                <span className="text-[10px] text-slate-700">
                    {documents.length}
                </span>

            </div>


            {/* Document list */}

            <div className="mb-3 max-h-32 overflow-y-auto">

                <div className="space-y-1">

                    {documents.map((document) => (
                        <div
                            key={document.id}
                            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-slate-500"
                        >

                            <span className="shrink-0 text-[10px] text-red-400">
                                PDF
                            </span>

                            <span className="min-w-0 truncate">
                                {document.doc_name}
                            </span>

                            {document.status === "ready" && (
                                <span className="ml-auto h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                            )}

                        </div>
                    ))}

                    {documents.length === 0 && (
                        <p className="px-2 py-1 text-xs text-slate-700">
                            No documents uploaded.
                        </p>
                    )}

                </div>

            </div>


            {/* Hidden file input */}

            <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
            />


            {/* Upload button */}

            <button
                type="button"
                disabled={
                    uploading ||
                    conversationId === null
                }
                onClick={() =>
                    fileInputRef.current?.click()
                }
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-white/[0.1] bg-white/[0.02] px-3 py-2 text-xs font-medium text-slate-500 transition hover:border-violet-500/40 hover:bg-violet-500/[0.04] hover:text-violet-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {uploading ? (
                    <>
                        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-slate-700 border-t-violet-400" />
                        Uploading...
                    </>
                ) : (
                    <>
                        <span className="text-base">
                            +
                        </span>

                        Upload Document
                    </>
                )}
            </button>


            {/* Error */}

            {error && (
                <p className="mt-2 truncate text-[11px] leading-4 text-red-400">
                    {error}
                </p>
            )}

        </div>
    );
}