import type { ReactNode } from "react";
import { Navigate } from "react-router";
import { isLoggedIn } from "./session";
import { getProtectedRouteRedirect } from "../site-config";

type ProtectedGateProps = {
  children: ReactNode;
  redirectTo?: string;
};

export function ProtectedGate({ children, redirectTo = getProtectedRouteRedirect() }: ProtectedGateProps) {
  if (!isLoggedIn()) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
