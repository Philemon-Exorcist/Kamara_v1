import { DashboardSidebar, DashboardTopbar } from "./dash-component";
import { BookOpen, BrainCircuit, FlaskConical, Atom, Grid3X3, Calculator } from "lucide-react";
import { useState, useMemo, type ReactNode } from "react";
import { useNavigate } from "react-router";
import { getGeneratedCourseStorageKey, submitCoursePrompt } from "./genie-api";
import CourseModal from "./ongoing/courseModal";

type Course = {
  title: string;
  icon: ReactNode;
  description: string;
};

const courses = [
  { title: "Mathematics", icon: <BookOpen size={24} />, description: "Learn the fundamentals of Mathematics." },
  { title: "Physics", icon: <Atom size={24} />, description: "Explore the strange world of Physics." },
  { title: "Chemistry", icon: <FlaskConical size={24} />, description: "Understand the structure, properties, and reactions of organic compounds." },
  { title: "Linear Algebra", icon: <Grid3X3 size={24} />, description: "Master vectors, matrices, and linear transformations." },
  { title: "Calculus II", icon: <Calculator size={24} />, description: "Continue your journey into the world of calculus." },
  { title: "AI for Beginners", icon: <BrainCircuit size={24} />, description: "An introduction to the concepts of Artificial Intelligence." },
] satisfies Course[];
export function meta() {
  return [
    { title: "Courses | Kamara AI" },
    {
      name: "description",
      content: "Browse and manage your courses.",
    },
  ];
}

export default function CoursesPage() {
  const navigate = useNavigate();
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [submitError, setSubmitError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filteredCourses = useMemo(() => {
    if (!searchQuery) {
      return courses;
    }
    return courses.filter(
      (course) => course.title.toLowerCase().includes(searchQuery.toLowerCase()) || course.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  const handleCoursePromptSubmit = async ({ course, prompt, photos }: { course: Course; prompt: string; photos: File[] }) => {
    setIsSubmitting(true);
    setSubmitError("");

    try {
      const generatedCourse = await submitCoursePrompt({
        courseTitle: course.title,
        courseDescription: course.description,
        prompt,
        photos,
      });

      sessionStorage.setItem(
        getGeneratedCourseStorageKey(),
        JSON.stringify({
          course,
          prompt,
          generatedCourse,
        })
      );

      setSelectedCourse(null);
      navigate("/ongoing/learning");
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Could not send your prompt. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <DashboardSidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />
      <section className="md:ml-[300px] min-h-screen" aria-label="Courses">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} onSearchChange={setSearchQuery} />
        <div className="p-6">
          <h1 className="text-3xl font-bold text-slate-900 mb-6">Courses</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <button
                key={course.title}
                type="button"
                onClick={() => {
                  setSubmitError("");
                  setSelectedCourse(course);
                }}
                className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between text-left hover:shadow-lg transition-shadow focus:outline-none focus:ring-4 focus:ring-blue-100"
              >
                <div>
                  <div className="text-blue-600 mb-4">{course.icon}</div>
                  <h2 className="text-lg font-semibold text-slate-800 mb-2">{course.title}</h2>
                  <p className="text-sm text-slate-600 mb-4">{course.description}</p>
                </div>
                <span className="text-sm font-semibold text-blue-600 hover:text-blue-700 self-start">Open Course &rarr;</span>
              </button>
            ))}
            {filteredCourses.length === 0 && (
              <div className="col-span-full text-center py-12 text-slate-500">
                <p className="text-lg font-semibold">No courses found</p>
                <p>Try adjusting your search query.</p>
              </div>
            )}
          </div>
        </div>
      </section>
      <CourseModal
        course={selectedCourse}
        errorMessage={submitError}
        isLoading={isSubmitting}
        isOpen={Boolean(selectedCourse)}
        onClose={() => {
          if (!isSubmitting) {
            setSelectedCourse(null);
          }
        }}
        onSubmit={handleCoursePromptSubmit}
      />
    </main>
  );
}
