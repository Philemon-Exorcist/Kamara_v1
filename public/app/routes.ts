import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/landing-page.tsx"),
  route("login", "routes/auth/login.tsx"),
  route("signup", "routes/auth/signup.tsx"),
  route("dashboard", "routes/pages/dashboard.tsx"),
  route("ongoing/learning", "routes/pages/ongoing/learning.tsx"),
  route("courses", "routes/pages/courses.tsx"),
  route("recent-courses", "routes/pages/dash-component/recent-courses.tsx"),
] satisfies RouteConfig;
