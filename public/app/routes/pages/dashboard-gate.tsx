// import type { ReactNode } from "react";
// import { Navigate } from "react-router";
// import { isLoggedIn } from "../auth/session";
// import { getProtectedRouteRedirect } from "../site-config";

// type DashboardGateProps = {
//   children: ReactNode;
// };

// export function DashboardGate({ children }: DashboardGateProps) {
//   if (!isLoggedIn()) {
//     return <Navigate to={getProtectedRouteRedirect()} replace />;
//   }

//   return <>{children}</>;
// }
