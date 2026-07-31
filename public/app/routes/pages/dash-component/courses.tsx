import { DashboardSidebar, DashboardTopbar } from ".";
import { BookOpen, BrainCircuit, FlaskConical, Atom, Grid3X3, Calculator } from "lucide-react";
import { useState } from "react";

const courses = [
  { title: "Mathematics", icon: <BookOpen size={24} />, description: "Learn the fundamentals of managing human resources." },
  { title: "Physics", icon: <Atom size={24} />, description: "Explore the strange world of quantum mechanics." },
  { title: "Chemistry", icon: <FlaskConical size={24} />, description: "Understand the structure, properties, and reactions of organic compounds." },
  { title: "Linear Algebra", icon: <Grid3X3 size={24} />, description: "Master vectors, matrices, and linear transformations." },
  { title: "Calculus II", icon: <Calculator size={24} />, description: "Continue your journey into the world of calculus." },
  { title: "AI for Beginners", icon: <BrainCircuit size={24} />, description: "An introduction to the concepts of Artificial Intelligence." },
];
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
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <DashboardSidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />
      <section className="md:ml-[300px] min-h-screen" aria-label="Courses">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} />
        <div className="p-6">
          <h1 className="text-3xl font-bold text-slate-900 mb-6">Courses</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div key={course.title} className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between hover:shadow-lg transition-shadow">
                <div>
                  <div className="text-blue-600 mb-4">{course.icon}</div>
                  <h2 className="text-lg font-semibold text-slate-800 mb-2">{course.title}</h2>
                  <p className="text-sm text-slate-600 mb-4">{course.description}</p>
                </div>
                <a href="/ongoing/learning" className="text-sm font-semibold text-blue-600 hover:text-blue-700 self-start">
                  View Course &rarr;
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
