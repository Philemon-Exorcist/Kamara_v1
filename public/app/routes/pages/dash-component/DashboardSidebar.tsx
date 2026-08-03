import { Calculator, ArrowLeft, Plus, Settings, CircleHelp, GraduationCap, LogOut, X, History, Sparkles, ChevronRight, BadgeInfo } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router";
import { clearSession, getSessionUserName } from "../../auth/session";

const navItems = ["Dashboard", "Genie", "Recent Sessions"];

const iconMap: Record<string, React.ReactNode> = {
  Dashboard: <GraduationCap size={18} />,
  Genie: <Sparkles size={18} />,
  "Recent Sessions": <History size={18} />,
  "Courses": <Calculator size={18} />,
  "Recent Courses": <History size={18} />,
};

interface DashboardSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  userName?: string;
  planTier?: string;
}

export function DashboardSidebar({ isOpen, onClose, userName: remoteUserName, planTier }: DashboardSidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const userName = remoteUserName || getSessionUserName();
  const planLabel = planTier ? `${planTier.charAt(0).toUpperCase()}${planTier.slice(1)} plan` : "No active plan";

  const handleLogout = () => {
    clearSession();
    navigate("/login");
  };

  const isActiveRoute = (href: string) => {
    if (href === "/dashboard") {
      return location.pathname === "/dashboard";
    }

    return location.pathname === href || location.pathname.startsWith(`${href}/`);
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
        className={`fixed inset-y-0 left-0 w-[232px] h-screen bg-white/95 backdrop-blur-xl border-r border-slate-200 shadow-[0_20px_60px_rgba(15,23,42,0.12)] px-2 py-2 overflow-hidden z-40 transform transition-transform duration-300 md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
        aria-label="Dashboard navigation"
      >
        <div className="flex h-full flex-col">
          <div className="rounded-[22px] border border-slate-200 bg-white px-2 py-2 shadow-sm">
            <div className="flex items-center justify-between">
              <a className="inline-flex items-center gap-2 text-[14px] font-semibold text-slate-900" href="/dashboard" aria-label="Kamara AI dashboard">
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-2xl bg-blue-600 text-white shadow-sm">
                  <GraduationCap size={14} />
                </span>
                Kamara
              </a>
              <button onClick={onClose} className="md:hidden rounded-2xl p-1.5 text-slate-500 hover:bg-slate-100" aria-label="Close sidebar">
                <X size={16} />
              </button>
            </div>

            <div className="mt-2.5 rounded-[18px] bg-slate-50 px-2.5 py-2">
              <p className="text-[8px] font-semibold uppercase tracking-[0.28em] text-slate-400">Menu</p>
              <div className="mt-2">
                <p className="truncate text-[12px] font-semibold text-slate-900">{userName}</p>
                <a className="mt-1 inline-flex items-center gap-1.5 text-[12px] font-semibold text-blue-700" href="/">
                  <ArrowLeft size={13} aria-hidden="true" />
                  Back
                </a>
              </div>
            </div>
          </div>

          <div className="mt-2 flex-1 min-h-0 overflow-y-auto pr-1">
            <p className="px-1.5 pb-0.5 pt-0 text-[8px] font-semibold uppercase tracking-[0.28em] text-slate-400">Menu</p>
            <nav className="space-y-1">
              {navItems.map((item) => {
                let href = `/${item.toLowerCase().replaceAll(" ", "-")}`;
                if (item === "Dashboard") {
                  href = "/dashboard";
                } else if (item === "Genie") {
                  href = "/courses";
                } else if (item === "Recent Sessions") {
                  href = "/recent-sessions";
                }
                const isActive = isActiveRoute(href);
                return (
                  <Link
                    className={`group flex items-center gap-2 rounded-[16px] px-2.5 py-1.75 text-[12px] transition ${
                      isActive
                        ? "bg-blue-50 text-blue-700 font-semibold shadow-[inset_4px_0_0_0_#2563eb]"
                        : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                    }`}
                    key={item}
                    to={href}
                  >
                    <span className={isActive ? "text-blue-700" : "text-slate-400 group-hover:text-blue-700"}>{iconMap[item]}</span>
                    {item}
                    {isActive ? <span className="ml-auto inline-flex h-1.5 w-1.5 rounded-full bg-blue-600" /> : <ChevronRight size={11} className="ml-auto opacity-0 transition group-hover:opacity-100" />}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="mt-2 space-y-1.5">
            <p className="px-1.5 pb-0.5 text-[8px] font-semibold uppercase tracking-[0.28em] text-slate-400">General</p>
            <a className="flex items-center gap-2 rounded-[16px] px-2.5 py-1.75 text-[12px] text-slate-500 hover:bg-slate-50 hover:text-slate-900" href="#settings">
              <Settings size={14} aria-hidden="true" />
              Settings
            </a>
            <a className="flex items-center gap-2 rounded-[16px] px-2.5 py-1.75 text-[12px] text-slate-500 hover:bg-slate-50 hover:text-slate-900" href="#support">
              <CircleHelp size={14} aria-hidden="true" />
              Supports
            </a>
            <button onClick={handleLogout} className="w-full flex items-center gap-2 rounded-[16px] px-2.5 py-1.75 text-[12px] text-slate-500 hover:bg-slate-50 hover:text-slate-900" type="button">
              <LogOut size={14} aria-hidden="true" />
              Log Out
            </button>
          </div>

          <div className="mt-2 rounded-[20px] bg-slate-950 p-2.5 text-white shadow-[0_18px_40px_rgba(15,23,42,0.28)]">
            <div className="flex items-start gap-3">
              <span className="inline-flex h-7.5 w-7.5 shrink-0 items-center justify-center rounded-2xl bg-blue-600 text-white">
                <BadgeInfo size={14} />
              </span>
              <div className="min-w-0">
                <p className="text-[12px] font-semibold">Current Plan</p>
                <p className="mt-0.5 text-[10px] text-slate-300">{planLabel}</p>
              </div>
            </div>
            <div className="mt-2 rounded-[16px] border border-white/10 bg-white/5 px-2.5 py-1.75">
              <p className="text-[8px] uppercase tracking-[0.24em] text-slate-400">Status</p>
              <p className="mt-1 text-[12px] font-semibold text-white">{planTier ? "Active" : "Unassigned"}</p>
            </div>
            <a
              className="mt-2.5 inline-flex w-full items-center justify-center gap-2 rounded-[16px] bg-blue-600 px-3 py-1.75 text-[12px] font-semibold text-white transition hover:bg-blue-700"
              href="/#pricing"
            >
              <Plus size={13} aria-hidden="true" />
              Upgrade Plan
            </a>
          </div>
        </div>
      </aside>
    </>
  );
}
