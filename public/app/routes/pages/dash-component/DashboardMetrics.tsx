import { Award, BookOpenCheck, Clock3, ListTodo } from "lucide-react";
import type { DashboardSummary } from "../dashboard-api";

interface DashboardMetricsProps {
  dashboard?: DashboardSummary | null;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US").format(value);
}

export function DashboardMetrics({ dashboard }: DashboardMetricsProps) {
  const recentActivityCount = dashboard?.recent_activity.length ?? 0;
  const completedCount = dashboard?.recent_activity.filter((item) => item.type === "exam").length ?? 0;
  const pendingCount = dashboard?.recommended_topics.length ?? 0;
  const enrolledCount = Math.max(recentActivityCount, pendingCount);

  const metrics = [
    {
      label: "Enrolled Classes",
      value: formatNumber(enrolledCount),
      note: "Derived from your dashboard activity",
      icon: <BookOpenCheck size={20} />,
      tone: "bg-emerald-600 text-white",
    },
    {
      label: "Completed",
      value: formatNumber(completedCount),
      note: "Finished learning tasks and quizzes",
      icon: <Award size={20} />,
      tone: "bg-slate-950 text-white",
    },
    {
      label: "Pending",
      value: formatNumber(pendingCount),
      note: "Recommended topics waiting for you",
      icon: <Clock3 size={20} />,
      tone: "bg-white text-slate-900",
    },
    {
      label: "Recent Activity",
      value: formatNumber(recentActivityCount),
      note: "Latest actions from your dashboard",
      icon: <ListTodo size={20} />,
      tone: "bg-white text-slate-900",
    },
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Dashboard metrics">
      {metrics.map((metric) => (
        <article key={metric.label} className={`rounded-[1.75rem] border border-slate-200 p-5 shadow-sm ${metric.tone}`}>
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold opacity-80">{metric.label}</p>
              <p className="mt-3 text-3xl font-semibold leading-none">{metric.value}</p>
            </div>
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-white/15">
              {metric.icon}
            </span>
          </div>
          <p className="mt-4 text-sm opacity-80">{metric.note}</p>
        </article>
      ))}
    </section>
  );
}
