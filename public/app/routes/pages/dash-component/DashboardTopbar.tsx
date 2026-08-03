import { Bell, Menu, Search } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { getSessionUser, getSessionUserName } from "../../auth/session";

interface DashboardTopbarProps {
  onMenuClick: () => void;
  onSearchChange?: (query: string) => void;
  userName?: string;
  planTier?: string;
  showSearch?: boolean;
  title?: string;
}

export function DashboardTopbar({
  onMenuClick,
  onSearchChange,
  userName: remoteUserName,
  planTier,
  showSearch = true,
  title = "Dashboard",
}: DashboardTopbarProps) {
  const [storedUserName, setStoredUserName] = useState("User");
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const user = getSessionUser();
    setStoredUserName(getSessionUserName("User"));
    setUserEmail(user?.email || "");
  }, []);

  const userName = remoteUserName || storedUserName;
  const userInitial = userName.charAt(0).toUpperCase();
  const planLabel = planTier ? `${planTier.charAt(0).toUpperCase()}${planTier.slice(1)} plan` : userEmail;

  return (
    <header className="fixed top-0 left-0 right-0 z-20 w-full border-b border-blue-100 bg-white/95 px-4 py-4 shadow-sm backdrop-blur sm:px-6 md:left-[232px] md:w-[calc(100%-232px)]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          <button onClick={onMenuClick} className="md:hidden -ml-2 rounded-full p-2 text-slate-700 transition hover:bg-blue-50 hover:text-blue-700" aria-label="Open sidebar">
            <Menu size={20} />
          </button>

          {showSearch ? <SearchForm onSearchChange={onSearchChange} /> : <DashboardTitle title={title} />}
        </div>

        <div className="flex items-center gap-3 sm:gap-4">
          <button className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-blue-100 bg-white text-slate-700 shadow-sm transition hover:bg-blue-50 hover:text-blue-700" type="button" aria-label="Notifications">
            <Bell size={18} />
          </button>

          <div className="inline-flex items-center gap-3 rounded-full border border-blue-100 bg-white px-3 py-2 shadow-sm sm:px-4">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-semibold text-white">{userInitial}</span>
            <div className="min-w-0 text-sm">
              <strong className="block max-w-40 truncate text-slate-900">{userName}</strong>
              {planLabel && <small className="block max-w-40 truncate text-slate-500">{planLabel}</small>}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function DashboardTitle({ title }: { title: string }) {
  return (
    <div className="min-w-0">
      <h1 className="truncate text-2xl font-semibold tracking-tight text-blue-700 sm:text-3xl">{title}</h1>
      <p className="mt-1 hidden truncate text-sm text-slate-500 sm:block">Plan, prioritize, and accomplish your tasks with ease.</p>
    </div>
  );
}

function SearchForm({ onSearchChange }: { onSearchChange?: (query: string) => void }) {
  const [query, setQuery] = useState("");

  const handleFormSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSearchChange?.(query);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    onSearchChange?.(newQuery);
  };

  return (
    <form onSubmit={handleFormSubmit} className="w-full">
      <label className="flex w-full items-center gap-3 rounded-full border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700 focus-within:ring-2 focus-within:ring-blue-200">
        <Search size={18} aria-hidden="true" className="text-blue-700" />
        <input
          id="dashboard-search"
          type="search"
          placeholder="Search on this page..."
          className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
          value={query}
          onChange={handleInputChange}
        />
      </label>
    </form>
  );
}
