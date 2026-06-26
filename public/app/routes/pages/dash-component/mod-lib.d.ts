import type { ReactNode } from "react";

export type ModuleTopic = {
  id: string;
  title: string;
  duration: string;
};

export type LearningModule = {
  id: string;
  title: string;
  type: "video" | "ai_lesson" | "assessment";
  count: number;
  countLabel: string;
  status: "new" | "in_progress" | "completed";
  topics: ModuleTopic[];
};

export const placeholderModules: LearningModule[];

export function buildModulesFromBackendResponse(generatedCourse: any): LearningModule[];

export default function ModuleLibrary(props: {
  modules?: LearningModule[];
  onModuleSelect?: (module: LearningModule) => void;
  selectedModuleId?: string;
}): ReactNode;
