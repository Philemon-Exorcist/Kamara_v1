const ACCESS_TOKEN_KEY = "access_token";
const USER_KEY = "kamara_user";

export type SessionUser = {
  id?: string;
  email?: string;
  name?: string;
  full_name?: string;
  [key: string]: unknown;
};

export type LoginSessionPayload = {
  access_token?: string;
  token?: string;
  user?: SessionUser;
  email?: string;
  name?: string;
  full_name?: string;
  id?: string;
  user_id?: string;
  [key: string]: unknown;
};

function canUseBrowserStorage() {
  return typeof window !== "undefined" && typeof localStorage !== "undefined";
}

export function getAccessToken() {
  if (!canUseBrowserStorage()) {
    return null;
  }

  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getSessionUser(): SessionUser | null {
  if (!canUseBrowserStorage()) {
    return null;
  }

  const storedUser = localStorage.getItem(USER_KEY);

  if (!storedUser) {
    return null;
  }

  try {
    return JSON.parse(storedUser) as SessionUser;
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function getSessionUserName(fallback = "Student") {
  const user = getSessionUser();
  return user?.name || user?.full_name || user?.email || fallback;
}

export function getSessionUserKey() {
  const user = getSessionUser();
  return user?.id || user?.email || "anonymous";
}

export function isLoggedIn() {
  return Boolean(getAccessToken());
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function normalizeUser(data: LoginSessionPayload): SessionUser {
  const user = data.user && typeof data.user === "object" ? data.user : {};

  return {
    ...user,
    id: String(user.id ?? data.id ?? data.user_id ?? ""),
    email: String(user.email ?? data.email ?? ""),
    name: String(user.name ?? user.full_name ?? data.name ?? data.full_name ?? user.email ?? data.email ?? "Student"),
    full_name: String(user.full_name ?? user.name ?? data.full_name ?? data.name ?? ""),
  };
}

export function saveLoginSession(data: LoginSessionPayload) {
  if (!canUseBrowserStorage()) {
    return;
  }

  const token = data.access_token || data.token;

  if (!token) {
    throw new Error("Login succeeded but no access token was returned by the backend.");
  }

  localStorage.setItem(ACCESS_TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(normalizeUser(data)));
}

export function saveSessionUser(user: SessionUser) {
  if (!canUseBrowserStorage()) {
    return;
  }

  localStorage.setItem(USER_KEY, JSON.stringify(normalizeUser({ user })));
}

export function clearSession() {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  sessionStorage.clear();
}

export async function loadCurrentUser(fetchUser: () => Promise<SessionUser>) {
  const user = await fetchUser();
  saveSessionUser(user);
  return user;
}

export async function validateSession(fetchUser: (accessToken: string) => Promise<SessionUser>) {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const user = await fetchUser(token);
    saveSessionUser(user);
    return user;
  } catch {
    clearSession();
    return null;
  }
}
