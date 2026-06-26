import type { ReactNode } from "react";

type CourseModalCourse = {
  title: string;
  icon: ReactNode;
  description: string;
};

type CourseModalProps = {
  course: CourseModalCourse | null;
  errorMessage?: string;
  isLoading?: boolean;
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (payload: { course: CourseModalCourse; prompt: string; photos: File[] }) => void;
};

export default function CourseModal(props: CourseModalProps): ReactNode;
