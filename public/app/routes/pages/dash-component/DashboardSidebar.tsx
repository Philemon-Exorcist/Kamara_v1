import { Calculator, ArrowLeft, Plus, Settings, CircleHelp, GraduationCap, LogOut, X, History } from "lucide-react";
import { useLocation, useNavigate } from "react-router";
import { clearSession, getSessionUserName } from "../../auth/session";

const navItems = ["Dashboard", "Courses", "Recent Courses"];

const iconMap: Record<string, React.ReactNode> = {
  Dashboard: <GraduationCap size={18} />,
  "Courses": <Calculator size={18} />,
  "Recent Courses": <History size={18} />,
};

interface DashboardSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  userName?: string;
}

export function DashboardSidebar({ isOpen, onClose, userName: remoteUserName }: DashboardSidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const userName = remoteUserName || getSessionUserName();

  const handleLogout = () => {
    clearSession();
    navigate("/login");
  };

  return (
    <>
      {/* Backdrop for mobile */}
      <div
        className={`fixed inset-0 bg-black bg-opacity-30 z-30 md:hidden transition-opacity ${isOpen ? "opacity-100" : "opacity-0 pointer-events-none"}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        className={`fixed inset-y-0 left-0 w-[300px] h-screen bg-white border-r border-slate-200 shadow-xl px-5 py-5 overflow-hidden z-40 transform transition-transform md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
        aria-label="Dashboard navigation"
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between mb-8">
            <a className="inline-flex items-center gap-3 text-xl font-semibold text-slate-900" href="/dashboard" aria-label="Kamara AI dashboard">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-2xl bg-blue-600 text-white shadow-sm">
                <GraduationCap size={18} />
              </span>
              Kamara
            </a>
            <button onClick={onClose} className="md:hidden p-2 -mr-2" aria-label="Close sidebar">
              <X size={20} />
            </button>
          </div>

          <div>
            <div className="mb-2">
              <p className="text-sm text-slate-500 mb-1">Your learning hub</p>
              <p className="mb-3 truncate text-sm font-semibold text-slate-900">{userName}</p>
              <a className="inline-flex items-center gap-2 text-sm text-blue-700 font-semibold" href="/">
                <ArrowLeft size={16} aria-hidden="true" />
                Back
              </a>
            </div>

            <div className="mb-4">
              <a href="../courses" className="w-full inline-flex items-center justify-center gap-2 rounded-3xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 transition">
                <Plus size={18} aria-hidden="true" />
                New Session
              </a>
            </div>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto">
            <nav className="space-y-1">
              {navItems.map((item) => {
                const href = item === "Dashboard" ? "/dashboard" : `/${item.toLowerCase().replaceAll(" ", "-")}`;
                const isActive = location.pathname === href;
                return (
                  <a
                    className={`flex items-center gap-3 rounded-3xl px-4 py-3 text-sm ${isActive ? "bg-blue-50 text-blue-700 font-semibold" : "text-slate-700 hover:bg-slate-100"}`}
                    href={href}
                    key={item}
                  >
                    <span className="text-slate-500">{iconMap[item]}</span>
                    {item}
                  </a>
                );
              })}
            </nav>
          </div>

          <div className="mt-auto pt-6">
            <a className="flex items-center gap-3 rounded-3xl px-4 py-3 text-sm text-slate-700 hover:bg-slate-100" href="#settings">
              <Settings size={18} aria-hidden="true" />
              Settings
            </a>
            <a className="flex items-center gap-3 rounded-3xl px-4 py-3 text-sm text-slate-700 hover:bg-slate-100" href="#support">
              <CircleHelp size={18} aria-hidden="true" />
              Supports
            </a>
            <button onClick={handleLogout} className="w-full flex items-center gap-3 rounded-3xl px-4 py-3 text-sm text-slate-700 hover:bg-slate-100" type="button">
              <LogOut size={18} aria-hidden="true" />
              Log Out
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
