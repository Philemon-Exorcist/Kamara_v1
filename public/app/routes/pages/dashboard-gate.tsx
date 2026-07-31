import type { ReactNode } from "react";
import { Navigate } from "react-router";
import { isLoggedIn } from "../auth/session";

type DashboardGateProps = {
  children: ReactNode;
};

export function DashboardGate({ children }: DashboardGateProps) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
