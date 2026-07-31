export const LOCAL_API_URL = "http://localhost:8001/api/v1";
export const PRODUCTION_API_URL = import.meta.env.VITE_API_BASE_URL || "https://kamara.onrender.com/api/v1";
export const LOCAL_WS_URL = "ws://localhost:8001/ws/api/v1";
export const PRODUCTION_WS_URL = import.meta.env.VITE_WS_BASE_URL || "wss://kamara.onrender.com/ws/api/v1";

/**
 * Determines the correct API base URL based on the current environment.
 */
export function getBaseUrl() {
  if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
    return LOCAL_API_URL;
  }
    return PRODUCTION_API_URL;
}

export function getWebSocketBaseUrl() {
  if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
    return LOCAL_WS_URL;
  }

  return PRODUCTION_WS_URL;
}
