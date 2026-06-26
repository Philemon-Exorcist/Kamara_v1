import { Clock, MessageCircleQuestion, Star } from "lucide-react";

interface StatsCardsProps {
  stats?: {
    hours_studied: number;
    questions_asked: number;
    average_score: number;
  };
}

function buildStats(stats?: StatsCardsProps["stats"]) {
  return [
    {
      label: "Hours studied",
      value: stats ? `${stats.hours_studied}h` : "--",
      icon: <Clock size={20} />,
      note: "Total focused learning time tracked by Kamara.",
    },
    {
      label: "Questions asked",
      value: stats ? String(stats.questions_asked) : "--",
      icon: <MessageCircleQuestion size={20} />,
      note: "Tutor questions from your recent study activity.",
    },
    {
      label: "Average score",
      value: stats ? `${stats.average_score}/100` : "--",
      icon: <Star size={20} />,
      note: "Go to report",
      action: true,
    },
  ];
}

export function StatsCards({ stats }: StatsCardsProps) {
  const statCards = buildStats(stats);

  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3" aria-label="Learning stats">
      {statCards.map((stat) => (
        <article key={stat.label} className="rounded-4xl bg-white p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-500">{stat.label}</h2>
              <p className="mt-3 text-3xl font-semibold text-slate-900">{stat.value}</p>
            </div>
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-blue-50 text-blue-700">
              {stat.icon}
            </span>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            {stat.action ? <a href="#report" className="text-blue-700 font-medium">{stat.note}</a> : stat.note}
          </p>
        </article>
      ))}
    </section>
  );
}
