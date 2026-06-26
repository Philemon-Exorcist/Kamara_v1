import { CheckCircle2, Circle, ChevronDown } from "lucide-react";

const progressGroups = [
  {
    title: "To do",
    items: [
      ["Rational inequalities. AI Assessment #5", "30 Mar, 2024"],
      ["AI about Homestage. Quiz", "28 Mar, 2024"],
      ["Shapes and Structures", "03 Apr, 2024"],
      ["Word Wonders: Unraveling Language", "03 Apr, 2024"],
    ],
  },
  {
    title: "On review",
    items: [
      ["Historical Chronicles: Exploring the Past", "30 Mar, 2024"],
      ["Epoch Explorations: Unraveling Timelines", "30 Mar, 2024"],
    ],
  },
  {
    title: "Completed",
    complete: true,
    items: [
      ["Physics Phantoms: Unveiling the Laws of Nature", "25 Mar, 2024"],
      ["Language Landscapes: Learning Vocabulary", "24 Mar, 2024"],
    ],
  },
];

export function HomeworkProgress() {
  return (
    <aside className="rounded-4xl bg-white p-6 shadow-sm border border-slate-200" aria-labelledby="homework-progress-title">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 id="homework-progress-title" className="text-lg font-semibold text-slate-900">Homework progress</h2>
          <p className="text-sm text-slate-500">Track your assignments and review status.</p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-3xl bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100 transition"
        >
          All
          <ChevronDown size={14} />
        </button>
      </div>

      <div className="mt-6 space-y-5">
        {progressGroups.map((group) => (
          <section key={group.title} className="space-y-3">
            <div className="rounded-3xl bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700">{group.title}</div>
            <div className="space-y-3">
              {group.items.map(([title, date]) => (
                <article key={title} className="flex items-center justify-between gap-4 rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-center gap-3">
                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-white text-blue-700 shadow-sm">
                      {group.complete ? <CheckCircle2 size={18} /> : <Circle size={18} />}
                    </span>
                    <div>
                      <h4 className="font-semibold text-slate-900">{title}</h4>
                      <p className="text-sm text-slate-500">Deadline: {date}</p>
                    </div>
                  </div>
                  <span className="text-sm text-slate-500">{group.complete ? "Done" : "Pending"}</span>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </aside>
  );
}
