export const LOCAL_API_URL = "http://localhost:8001/api/v1";
export const PRODUCTION_API_URL = "https://kamara.onrender.com";

/**
 * Determines the correct API base URL based on the current environment.
 */
export function getBaseUrl() {
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return LOCAL_API_URL;
  }

  return PRODUCTION_API_URL;
}