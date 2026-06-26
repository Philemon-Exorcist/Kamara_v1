import { getAuthHeaders } from "../auth/session";

const LOCAL_API_URL = "http://localhost:8001/api/v1";
const PRODUCTION_API_URL = "https://kamsi-xza9.onrender.com/api/v1";

export type DashboardSummary = {
  full_name: string;
  plan_tier: string;
  stats: {
    hours_studied: number;
    questions_asked: number;
    average_score: number;
  };
  recent_activity: Array<{
    id: string;
    type: string;
    title: string;
    timestamp: string;
  }>;
  recommended_topics: string[];
};

export type DashboardSession = {
  id: string;
  subject?: string;
  course?: string;
  topic?: string;
  user_prompt?: string;
  generated_notes?: string;
  created_at?: string;
  is_active?: boolean;
};

type DashboardSessionsResponse = {
  status: string;
  total_sessions: number;
  sessions: DashboardSession[];
};

function getBaseUrl() {
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return LOCAL_API_URL;
  }

  return PRODUCTION_API_URL;
}

async function parseApiError(response: Response, fallback: string) {
  const errorData = await response.json().catch(() => ({}));
  return typeof errorData.detail === "string" ? errorData.detail : fallback;
}

async function dashboardFetch<T>(path: string, fallback: string): Promise<T> {
  const response = await fetch(`${getBaseUrl()}${path}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response, fallback));
  }

  return response.json();
}

export const dashboardApi = {
  getSummary() {
    return dashboardFetch<DashboardSummary>("/pages/dashboard", "Could not load your dashboard.");
  },

  getSessions() {
    return dashboardFetch<DashboardSessionsResponse>("/dashboard/sessions", "Could not load your recent courses.");
  },
};
