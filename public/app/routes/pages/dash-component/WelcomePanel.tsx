import { getSessionUserName } from "../../auth/session";

interface WelcomePanelProps {
  fullName?: string;
  planTier?: string;
  recommendations?: string[];
}

export function WelcomePanel({ fullName, planTier, recommendations = [] }: WelcomePanelProps) {
  const userName = fullName || getSessionUserName();
  const planLabel = planTier ? `${planTier.charAt(0).toUpperCase()}${planTier.slice(1)} plan` : "Student dashboard";
  const panelItems = recommendations.length > 0 ? recommendations.slice(0, 2) : ["Your recommendations will appear here once your dashboard loads.", "Start a new session to build your learning plan."];

  return (
    <section className="rounded-4xl bg-white p-8 shadow-sm border border-slate-200">
      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Student dashboard</p>
            <h1 id="dashboard-welcome-title" className="mt-3 text-3xl font-semibold text-slate-900">Welcome back, {userName}</h1>
          </div>
          <div className="rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700">{planLabel}</div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          {panelItems.map((item, index) => (
            <p key={item} className={`rounded-3xl p-5 text-slate-600 ${index === 0 ? "bg-blue-50" : "bg-slate-50"}`}>
              {item}
            </p>
          ))}
        </div>
      </div>
    </section>
  );
}
