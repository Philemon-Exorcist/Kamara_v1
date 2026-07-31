import { useEffect, useState, type ReactNode } from "react";
import { Navigate } from "react-router";
import { authApi } from "./auth-api";
import { validateSession } from "./session";
import { getProtectedRouteRedirect } from "../site-config";

type ProtectedGateProps = {
  children: ReactNode;
  redirectTo?: string;
};

export function ProtectedGate({ children, redirectTo = getProtectedRouteRedirect() }: ProtectedGateProps) {
  const [isChecking, setIsChecking] = useState(true);
  const [isAllowed, setIsAllowed] = useState(false);

  useEffect(() => {
    let ignore = false;

    validateSession((accessToken) => authApi.me(accessToken))
      .then((user) => {
        if (ignore) {
          return;
        }

        setIsAllowed(Boolean(user));
        setIsChecking(false);
      })
      .catch(() => {
        if (ignore) {
          return;
        }

        setIsAllowed(false);
        setIsChecking(false);
      });

    return () => {
      ignore = true;
    };
  }, []);

  if (isChecking) {
    return null;
  }

  if (!isAllowed) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}
