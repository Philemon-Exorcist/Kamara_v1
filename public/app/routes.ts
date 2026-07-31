import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/landing-page.tsx"),
  route("login", "routes/auth/login.tsx"),
  route("signup", "routes/auth/signup.tsx"),
  route("forgot-password", "routes/auth/forgot-password.tsx"),
  route("update-password", "routes/auth/update-password.tsx"),
  route("reset-password", "routes/auth/reset-password.tsx"),
  route("dashboard", "routes/pages/dashboard.tsx"),
  route("ongoing/learning", "routes/pages/ongoing/learning.tsx"),
  route("courses", "routes/pages/genie.tsx"),
  route("recent-sessions", "routes/pages/dash-component/recent-sessions.tsx"),
] satisfies RouteConfig;
