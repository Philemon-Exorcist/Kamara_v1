import { useState } from "react";
import { getSessionUserName } from "../../auth/session";
import physicsCardImage from "../../../assets/hero1.jpg";
import chemistryCardImage from "../../../assets/hero2.jpg";

interface WelcomePanelProps {
  fullName?: string;
  planTier?: string;
  recommendations?: string[];
}

type TabKey = "in-progress" | "upcoming" | "completed";

type CourseCard = {
  title: string;
  teacher: string;
  progressLabel: string;
  image: string;
  accent: string;
};

export function WelcomePanel({ fullName, planTier }: WelcomePanelProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("in-progress");
  const userName = fullName || getSessionUserName();
  const planLabel = planTier ? `${planTier.charAt(0).toUpperCase()}${planTier.slice(1)} plan` : "Student dashboard";

  const inProgressClasses: CourseCard[] = [
    {
      title: "Fundamentals of Physics",
      teacher: "John Doe",
      progressLabel: "Today • 11:30am",
      image: physicsCardImage,
      accent: "bg-emerald-700/90",
    },
    {
      title: "Fundamentals of Chemistry",
      teacher: "John Doe",
      progressLabel: "90 mins",
      image: chemistryCardImage,
      accent: "bg-emerald-700/90",
    },
  ];

  const upcomingClasses: CourseCard[] = [
    {
      title: "English Comprehension",
      teacher: "John Doe",
      progressLabel: "Tomorrow",
      image: physicsCardImage,
      accent: "bg-blue-700/90",
    },
    {
      title: "World History",
      teacher: "John Doe",
      progressLabel: "Next week",
      image: chemistryCardImage,
      accent: "bg-blue-700/90",
    },
  ];

  const completedClasses: CourseCard[] = [
    {
      title: "Introduction to Algebra",
      teacher: "John Doe",
      progressLabel: "Completed",
      image: chemistryCardImage,
      accent: "bg-slate-700/90",
    },
    {
      title: "Basic Biology",
      teacher: "John Doe",
      progressLabel: "Completed",
      image: physicsCardImage,
      accent: "bg-slate-700/90",
    },
  ];

  const activeClasses =
    activeTab === "completed" ? completedClasses : activeTab === "upcoming" ? upcomingClasses : inProgressClasses;

  return (
    <section className="w-full overflow-hidden rounded-4xl border border-slate-200 bg-white shadow-sm" aria-labelledby="dashboard-welcome-title">
      <div className="flex flex-col gap-4 p-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Student dashboard</p>
            <h1 id="dashboard-welcome-title" className="mt-3 text-3xl font-semibold text-slate-900">
              Welcome back, {userName}
            </h1>
          </div>
          <div className="rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700">{planLabel}</div>
        </div>

        <div className="flex flex-wrap items-center gap-6 border-b border-slate-200 pb-4">
          <button
            type="button"
            onClick={() => setActiveTab("in-progress")}
            className={`border-b-2 pb-2 text-lg font-semibold transition ${
              activeTab === "in-progress" ? "border-slate-900 text-slate-900" : "border-transparent text-slate-400"
            }`}
          >
            In Progress
          </button>
          <button
              type="button"
              onClick={() => setActiveTab("upcoming")}
              className={`border-b-2 pb-2 text-lg font-semibold transition ${
                activeTab === "upcoming" ? "border-slate-900 text-slate-900" : "border-transparent text-slate-400"
              }`}
            >
              Upcoming
            </button>
          <button
            type="button"
            onClick={() => setActiveTab("completed")}
            className={`border-b-2 pb-2 text-lg font-semibold transition ${
              activeTab === "completed" ? "border-slate-900 text-slate-900" : "border-transparent text-slate-400"
            }`}
          >
            Completed
          </button>
          <a
            href="/ongoing/learning"
            className="ml-auto inline-flex items-center rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
          >
            View more
          </a>
        </div>

        <div className="flex gap-4 overflow-x-auto pb-2 pr-1 snap-x snap-mandatory">
          {activeClasses.map((course) => (
            <article
              key={`${activeTab}-${course.title}`}
              className="group min-w-[320px] flex-none snap-start overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-950 shadow-sm transition-transform duration-300 hover:-translate-y-1 md:min-w-[380px]"
            >
              <div
                className="relative flex min-h-[210px] flex-col justify-between bg-cover bg-center p-4 text-white md:min-h-[190px]"
                style={{
                  backgroundImage: `linear-gradient(180deg, rgba(15, 23, 42, 0.25) 0%, rgba(15, 23, 42, 0.78) 100%), url(${course.image})`,
                }}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 rounded-full bg-black/30 px-3 py-2 backdrop-blur-md">
                    <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full border border-white/30 bg-white/20">
                      <span className="text-sm font-semibold">JD</span>
                    </div>
                    <div>
                      <p className="text-sm font-semibold leading-none">{course.teacher}</p>
                      <p className="text-xs text-white/70">Instructor</p>
                    </div>
                  </div>
                  <div className={`rounded-full px-3 py-1.5 text-xs font-semibold ${course.accent}`}>{course.progressLabel}</div>
                </div>

                <div className="rounded-2xl bg-black/35 px-4 py-3 backdrop-blur-sm">
                  <h2 className="text-xl font-semibold">{course.title}</h2>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
