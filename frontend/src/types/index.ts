export interface SignupResponse {
    message: string;
    user_id: string;
}

export interface SigninResponse {
    message: string;
    access_token: string;
    refresh_token: string;
    user_id: string;
}

export interface Conversation {
    id: number;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface Document {
    id: number;
    mime_type: string;
    page_count: number;
    status: string;
    updated_at: string;
    owner_id: string;
    doc_name: string;
    file_path: string;
    size_bytes: number;
    content_hash: string;
    created_at: string;
}

export interface Message {
    id: number;
    conversation_id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
}

export interface ResearchResponse {
    answer: string;
    citations: string[];
    grounded: boolean;
}

export interface CreateConversationRequest {
    title: string;
}

export interface MessageRequest {
    query: string;
}

export interface UploadDocumentResponse {
    message: string;
    document: {
        id: number;
        doc_name: string;
        status: string;
    };
}

export interface ConversationDocument {
    id: number;
    doc_name: string;
    mime_type: string;
    page_count: number;
    status: string;
    created_at: string;
}