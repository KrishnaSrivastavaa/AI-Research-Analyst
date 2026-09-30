import type {
  SignupResponse,
  SigninResponse,
  Conversation,
  Document,
  Message,
  ResearchResponse,
  UploadDocumentResponse,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL;

function getAccessToken(): string | null {
  return localStorage.getItem("access_token");
}

export async function signup(
  name: string,
  email: string,
  username: string,
  password: string,
): Promise<SignupResponse> {
  const response = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      email,
      username,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Signup failed");
  }

  return data;
}

export async function signin(
  email: string,
  password: string,
): Promise<SigninResponse> {
  const response = await fetch(`${API_URL}/auth/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Signin failed");
  }

  return data;
}

export async function getConversations(): Promise<Conversation[]> {
  const response = await authenticatedFetch(`${API_URL}/chat/conversations`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch conversations");
  }

  return data;
}

export async function createConversation(title: string): Promise<Conversation> {
  const response = await authenticatedFetch(`${API_URL}/chat/conversations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to create conversation");
  }

  return data;
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  const response = await authenticatedFetch(
    `${API_URL}/chat/conversations/${conversationId}/messages`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch messages");
  }

  return data;
}

export async function sendMessage(
  conversationId: number,
  query: string,
): Promise<ResearchResponse> {
  const response = await authenticatedFetch(
    `${API_URL}/chat/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to send message");
  }

  return data;
}

export async function getDocuments(): Promise<Document[]> {
  const response = await authenticatedFetch(`${API_URL}/doc/documents`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch documents");
  }

  return data;
}

export async function uploadDocument(
  file: File,
): Promise<UploadDocumentResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await authenticatedFetch(`${API_URL}/doc/documents`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to upload document");
  }

  return data;
}

export async function getConversationDocuments(conversationId: number) {
  const response = await authenticatedFetch(
    `${API_URL}/chat/conversations/${conversationId}/documents`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch conversation documents");
  }

  return data;
}

export async function addDocumentToConversation(
  conversationId: number,
  documentId: number,
) {
  const response = await authenticatedFetch(
    `${API_URL}/chat/conversations/${conversationId}/documents`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        document_id: documentId,
      }),
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to add document to conversation");
  }

  return data;
}

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_id");

      throw new Error(data.detail || "Session expired. Please sign in again.");
    }

    localStorage.setItem("access_token", data.access_token);

    localStorage.setItem("refresh_token", data.refresh_token);

    return data.access_token;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function authenticatedFetch(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  let token = getAccessToken();

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status !== 401) {
    return response;
  }

  token = await refreshAccessToken();

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
}
