import { DashboardSidebar, DashboardTopbar } from "./dash-component";
import { BrainCircuit, BookOpen } from "lucide-react";
import { useState } from "react";

const recentCourses = [
  { title: "Quantum Physics", icon: <BrainCircuit size={24} />, description: "Continue exploring the strange world of quantum mechanics.", lastAccessed: "2 hours ago" },
  { title: "Calculus II", icon: <BookOpen size={24} />, description: "Revisiting derivatives and integrals.", lastAccessed: "1 day ago" },
];

export function meta() {
  return [
    { title: "Recent Courses | Kamara AI" },
    {
      name: "description",
      content: "Access your recently viewed courses.",
    },
  ];
}

export default function RecentCoursesPage() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <DashboardSidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />
      <section className="md:ml-[300px] min-h-screen" aria-label="Recent Courses">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} />
        <div className="p-6">
          <h1 className="text-3xl font-bold text-slate-900 mb-6">Recent Courses</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentCourses.map((course) => (
              <div key={course.title} className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between hover:shadow-lg transition-shadow">
                <div>
                  <div className="text-blue-600 mb-4">{course.icon}</div>
                  <h2 className="text-lg font-semibold text-slate-800 mb-2">{course.title}</h2>
                  <p className="text-sm text-slate-600 mb-4">{course.description}</p>
                </div>
                <a href="/pages/ongoing/learning" className="text-sm font-semibold text-blue-600 hover:text-blue-700 self-start">
                  Continue Learning &rarr;
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
