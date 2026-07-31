import type { ReactNode } from "react";
import { Navigate } from "react-router";
import { isAuthFlowEnabled } from "../site-config";

type AuthGateProps = {
  children: ReactNode;
  redirectTo?: string;
};

export function AuthGate({ children, redirectTo = "/#footer" }: AuthGateProps) {
  if (!isAuthFlowEnabled()) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
