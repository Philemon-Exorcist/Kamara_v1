import { ChevronDown, PlayCircle } from "lucide-react";
import { useState } from "react";

export const placeholderModules = [
  {
    id: "module-foundations",
    title: "Course Foundations",
    type: "ai_lesson",
    count: 3,
    countLabel: "3 Topics",
    status: "new",
    topics: [
      { id: "foundation-overview", title: "Overview and learning goals", duration: "8 min" },
      { id: "foundation-key-terms", title: "Key terms and concepts", duration: "12 min" },
      { id: "foundation-practice", title: "Guided practice activity", duration: "15 min" },
    ],
  },
  {
    id: "module-core-lessons",
    title: "Core Lessons",
    type: "ai_lesson",
    count: 3,
    countLabel: "3 Topics",
    status: "new",
    topics: [
      { id: "core-introduction", title: "Introduction to the main idea", duration: "10 min" },
      { id: "core-examples", title: "Worked examples", duration: "18 min" },
      { id: "core-checkpoint", title: "Knowledge checkpoint", duration: "7 min" },
    ],
  },
  {
    id: "module-review",
    title: "Review and Assessment",
    type: "assessment",
    count: 3,
    countLabel: "3 Topics",
    status: "new",
    topics: [
      { id: "review-summary", title: "Summary notes", duration: "6 min" },
      { id: "review-quiz", title: "Short quiz", duration: "10 min" },
      { id: "review-next-steps", title: "Next steps", duration: "5 min" },
    ],
  },
];

function readArray(...values) {
  return values.find((value) => Array.isArray(value)) ?? [];
}

function normalizeTopic(topic, index, moduleId) {
  const title = topic?.title ?? topic?.name ?? topic?.topic ?? topic?.heading ?? `Topic ${index + 1}`;
  const duration = topic?.duration ?? topic?.time ?? topic?.estimated_duration ?? topic?.estimatedDuration ?? "10 min";

  return {
    id: String(topic?.id ?? `${moduleId}-topic-${index + 1}`),
    title: String(title),
    duration: String(duration),
  };
}

function normalizeModule(module, index) {
  const id = String(module?.id ?? module?.slug ?? `generated-module-${index + 1}`);
  const rawTopics = readArray(module?.topics, module?.subtopics, module?.lessons, module?.items, module?.content);
  const fallbackTopics = placeholderModules[index % placeholderModules.length].topics;
  const topics = rawTopics.length > 0 ? rawTopics.map((topic, topicIndex) => normalizeTopic(topic, topicIndex, id)) : fallbackTopics;
  const count = Number(module?.count ?? topics.length);

  return {
    id,
    title: String(module?.title ?? module?.name ?? module?.module_title ?? `Module ${index + 1}`),
    type: module?.type === "video" || module?.type === "assessment" ? module.type : "ai_lesson",
    count,
    countLabel: String(module?.countLabel ?? module?.count_label ?? `${count} Topic${count === 1 ? "" : "s"}`),
    status: module?.status === "completed" || module?.status === "in_progress" ? module.status : "new",
    topics,
  };
}

export function buildModulesFromBackendResponse(generatedCourse) {
  const modules = readArray(
    generatedCourse?.modules,
    generatedCourse?.data?.modules,
    generatedCourse?.course?.modules,
    generatedCourse?.lessons,
    generatedCourse?.outline
  );

  if (modules.length === 0) {
    return placeholderModules;
  }

  return modules.map(normalizeModule);
}

export default function ModuleLibrary({ modules = placeholderModules, onModuleSelect, selectedModuleId }) {
  const [openModuleId, setOpenModuleId] = useState(modules[0]?.id ?? "");

  return (
    <div className="space-y-3 p-5" id="learning">
      {modules.map((courseModule, index) => {
        const isSelected = selectedModuleId ? selectedModuleId === courseModule.id : index === 0;
        const isOpen = openModuleId === courseModule.id;

        return (
          <article
            className={`rounded-lg border transition ${
              isSelected ? "border-blue-600 bg-blue-50 text-slate-900" : "border-slate-200 bg-white text-slate-900 hover:border-blue-200"
            }`}
            key={courseModule.id}
          >
            <button
              className="flex w-full items-center justify-between gap-3 p-4 text-left"
              type="button"
              onClick={() => {
                setOpenModuleId(isOpen ? "" : courseModule.id);
                onModuleSelect?.(courseModule);
              }}
            >
              <span className="min-w-0">
                <strong className="block truncate text-sm">{courseModule.title}</strong>
                <small className="mt-1 block text-xs text-blue-600">{courseModule.countLabel}</small>
              </span>
              <ChevronDown size={18} aria-hidden="true" className={`shrink-0 text-blue-700 transition ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
              <div className="space-y-2 border-t border-blue-100 px-4 py-3">
                {courseModule.topics.map((topic) => (
                  <button
                    type="button"
                    key={topic.id}
                    className="flex w-full items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-sm transition hover:border-blue-200 hover:bg-blue-50"
                  >
                    <span className="inline-flex min-w-0 items-center gap-2">
                      <PlayCircle size={14} className="shrink-0 text-blue-600" aria-hidden="true" />
                      <span className="truncate">{topic.title}</span>
                    </span>
                    <span className="shrink-0 text-xs font-semibold text-slate-500">{topic.duration}</span>
                  </button>
                ))}
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
}
