import { CalendarDays } from "lucide-react";

const days = [
  { day: "Mon", date: "25" },
  { day: "Tue", date: "26" },
  { day: "Wed", date: "27" },
  { day: "Thu", date: "28", active: true },
  { day: "Fri", date: "29" },
  { day: "Sat", date: "30" },
  { day: "Sun", date: "31" },
];

const lessons = [
  {
    time: "08:00",
    title: "Algorithms",
    range: "08:00 - 08:50",
    tag: "Mathematics",
    type: "math",
    avatars: ["J", "A", "K"],
  },
  {
    time: "09:00",
    title: "Levels of organization of living things",
    range: "09:00 - 10:00",
    tag: "Biology",
    type: "bio",
    avatars: ["N", "S"],
  },
  {
    time: "10:00",
    title: "Break",
    range: "10:00 - 10:30",
    type: "break",
    avatars: [],
  },
];

export function SchedulePanel() {
  return (
    <section className="rounded-4xl bg-white p-6 shadow-sm border border-slate-200" aria-labelledby="schedule-title">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="inline-flex h-12 w-12 items-center justify-center rounded-3xl bg-blue-50 text-blue-700">
            <CalendarDays size={20} aria-hidden="true" />
          </span>
          <div>
            <h2 id="schedule-title" className="text-lg font-semibold text-slate-900">Timetable</h2>
            <p className="text-sm text-slate-500">Upcoming lessons for the week.</p>
          </div>
        </div>
        <time className="rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700" dateTime="2024-03-28">
          Mar 28, 2024
        </time>
      </div>

      <div className="mt-5 grid grid-cols-4 gap-3">
        {days.map((day) => (
          <button
            key={day.day}
            type="button"
            className={`rounded-3xl border px-3 py-3 text-center text-sm font-medium transition ${
              day.active ? "border-blue-200 bg-blue-50 text-blue-700 shadow-sm" : "border-slate-200 bg-slate-50 text-slate-700 hover:border-blue-200"
            }`}
          >
            <span className="block text-xs text-slate-500">{day.day}</span>
            <strong className="mt-1 block text-base">{day.date}</strong>
          </button>
        ))}
      </div>

      <div className="mt-6 space-y-4">
        {lessons.map((lesson) => (
          <article key={lesson.title} className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4 shadow-sm">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-slate-900">{lesson.title}</p>
                <p className="mt-2 text-sm text-slate-500">{lesson.range}</p>
              </div>
              <span className="rounded-3xl bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">{lesson.tag || "Break"}</span>
            </div>
            {lesson.avatars.length > 0 ? (
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
                <span>Participants:</span>
                <div className="inline-flex -space-x-2">
                  {lesson.avatars.map((avatar) => (
                    <span key={avatar} className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white text-xs shadow-sm">
                      {avatar}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
