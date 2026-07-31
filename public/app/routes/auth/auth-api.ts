import { getBaseUrl } from "../api-config";

async function parseApiError(response: Response, fallback: string) {
  const errorData = await response.json().catch(() => ({}));
  if (typeof errorData.detail === "string") {
    return errorData.detail;
  }

  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map((error: any) => {
        const field = Array.isArray(error.loc) ? error.loc.at(-1) : null;
        return field ? `${field}: ${error.msg}` : error.msg;
      })
      .filter(Boolean)
      .join(" ");
  }

  return fallback;
}

async function apiFetch(path: string, init: RequestInit) {
  try {
    return await fetch(`${getBaseUrl()}${path}`, init);
  } catch {
    throw new Error(
      "Could not reach the backend API. Please check your internet connection or try again later."
    );
  }
}

/**
 * Client-side validation logic for authentication inputs.
 */
export const validate = {
  email: (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) return "Email is required.";
    if (!re.test(email)) return "Please enter a valid email address.";
    return null;
  },
  password: (password: string, isSignup = false) => {
    if (!password) return "Password is required.";
    if (isSignup && password.length < 8) {
      return "Password must be at least 8 characters long for security.";
    }
    return null;
  },
  name: (name: string) => {
    if (!name || name.trim().length < 2) return "Please enter your full name.";
    return null;
  },
};

export type RecoveryCredentials = {
  accessToken?: string;
  refreshToken?: string;
  code?: string;
};

export const authApi = {
  async signup(credentials: { email: string; password: string; firstName: string; lastName: string }) {
    // 1. Perform client-side validation
    const firstNameErr = validate.name(credentials.firstName);
    const lastNameErr = validate.name(credentials.lastName);
    const emailErr = validate.email(credentials.email);
    const passErr = validate.password(credentials.password, true);
    if (firstNameErr) throw new Error(firstNameErr);
    if (lastNameErr) throw new Error(lastNameErr);
    if (emailErr) throw new Error(emailErr);
    if (passErr) throw new Error(passErr);

    // 2. Execute network request
    const payload = {
      email: credentials.email,
      password: credentials.password,
      first_name: credentials.firstName.trim(),
      last_name: credentials.lastName.trim(),
    };

    const response = await apiFetch("/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      throw new Error(await parseApiError(response, "Signup failed. The email might already be in use."));
    }
    // Upon success, the UI (signup.tsx) navigates to /login
    return response.json();
  },

  async login(credentials: { email: string; password: string }) {
    // 1. Basic validation
    const emailErr = validate.email(credentials.email);
    const passErr = validate.password(credentials.password);
    if (emailErr) throw new Error(emailErr);
    if (passErr) throw new Error(passErr);

    // 2. Execute network request
    const response = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Authentication failed. Please check your credentials."));
    }

    // Upon success, the UI (login.tsx) stores the token and navigates to /dashboard
    return response.json();
  },

  async forgotPassword(credentials: { email: string }) {
    const emailErr = validate.email(credentials.email);
    if (emailErr) throw new Error(emailErr);

    const response = await apiFetch("/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: credentials.email }),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "We could not start the password reset flow."));
    }

    return response.json();
  },

  async updatePassword(credentials: RecoveryCredentials & { newPassword: string }) {
    const passErr = validate.password(credentials.newPassword, true);
    if (passErr) throw new Error(passErr);

    const response = await apiFetch("/auth/update-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        access_token: credentials.accessToken,
        refresh_token: credentials.refreshToken,
        code: credentials.code,
        new_password: credentials.newPassword,
      }),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Failed to update password."));
    }

    return response.json();
  },

  async me(accessToken: string) {
    const response = await apiFetch("/auth/me", {
      method: "GET",
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Could not load your profile."));
    }

    return response.json();
  },

  async joinWaitlist(credentials: { email: string; name: string }) {
    const nameErr = validate.name(credentials.name);
    const emailErr = validate.email(credentials.email);
    if (nameErr) throw new Error(nameErr);
    if (emailErr) throw new Error(emailErr);

    const response = await apiFetch("/waitlist/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: credentials.email,
        full_name: credentials.name,
      }),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Failed to join waitlist."));
    }
    return response.json();
  },
};
