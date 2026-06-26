import type { Route } from "./+types/dashboard";
import { useEffect, useState } from "react";
import {
  DashboardSidebar,
  DashboardTopbar,
  EventsPanel,
  HomeworkProgress,
  SchedulePanel,
  StatsCards,
  WelcomePanel,
} from "./dash-component";
import { dashboardApi, type DashboardSummary } from "./dashboard-api";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Dashboard | Kamara AI" },
    {
      name: "description",
      content: "Kamara AI student learning dashboard.",
    },
  ];
}

export default function DashboardPage() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [dashboardError, setDashboardError] = useState("");

  useEffect(() => {
    let ignore = false;

    dashboardApi
      .getSummary()
      .then((data) => {
        if (!ignore) {
          setDashboard(data);
          setDashboardError("");
        }
      })
      .catch((error) => {
        if (!ignore) {
          setDashboardError(error instanceof Error ? error.message : "Could not load your dashboard.");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <DashboardSidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} userName={dashboard?.full_name} />

      <section className="md:ml-[300px] min-h-screen" aria-label="Student dashboard">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} onSearchChange={setSearchQuery} userName={dashboard?.full_name} planTier={dashboard?.plan_tier} />

        <div className="max-w-[1400px] mx-auto px-6 py-6">
          {dashboardError ? (
            <div className="mb-6 rounded-3xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-700">
              {dashboardError}
            </div>
          ) : null}

          <div className="grid gap-6 xl:grid-cols-[1.6fr_0.9fr]">
            <div className="space-y-6">
              <WelcomePanel fullName={dashboard?.full_name} planTier={dashboard?.plan_tier} recommendations={dashboard?.recommended_topics} />
              <StatsCards stats={dashboard?.stats} />

              <div className="grid gap-6 xl:grid-cols-2">
                <SchedulePanel />
                <EventsPanel activities={dashboard?.recent_activity} />
              </div>
            </div>

            <HomeworkProgress />
          </div>
        </div>
      </section>
    </main>
  );
}
