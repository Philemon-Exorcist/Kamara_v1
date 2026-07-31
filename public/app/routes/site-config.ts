export const AUTH_PAGES_ENABLED = (() => {
  const explicitToggle = import.meta.env.VITE_ENABLE_AUTH_PAGES;
  if (typeof explicitToggle === "string") {
    return explicitToggle.toLowerCase() === "true";
  }

  return true;
})();

export function isAuthFlowEnabled() {
  return AUTH_PAGES_ENABLED;
}

export const APP_PAGES_ENABLED = (() => {
  const explicitToggle = import.meta.env.VITE_ENABLE_APP_PAGES;
  if (typeof explicitToggle === "string") {
    return explicitToggle.toLowerCase() === "true";
  }

  return import.meta.env.DEV;
})();

export function isAppFlowEnabled() {
  return APP_PAGES_ENABLED;
}

export function getAuthCtaHref() {
  return isAuthFlowEnabled() ? "/signup" : "/#footer";
}

export function getAuthCtaLabel(defaultLabel: string) {
  return isAuthFlowEnabled() ? defaultLabel : "Join the waitlist";
}

export function getProtectedRouteRedirect() {
  return "/login";
}
