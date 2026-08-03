
export const PRODUCTION_API_URL = "https://kamara.onrender.com/api/v1";
export const PRODUCTION_WEBSOCKET_URL = "wss://kamara.onrender.com/ws/api/v1";
export const LOCAL_API_URL = "http://localhost:8001/api/v1";
//export const PRODUCTION_API_URL = "https://kamara.onrender.com";
export const LOCAL_WEBSOCKET_URL = "ws://localhost:8001/ws/api/v1";

/**
 * Frontend API base URL.
 */
export function getBaseUrl() {
  //return PRODUCTION_API_URL;
  return LOCAL_API_URL;
}

/**
 * Returns the websocket origin for the current environment.
 */
export function getWebSocketBaseUrl() {
  //return PRODUCTION_WEBSOCKET_URL;
  return LOCAL_WEBSOCKET_URL;
}


