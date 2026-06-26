import { Search, Bell, Menu } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { getSessionUser, getSessionUserName } from "../../auth/session";

interface DashboardTopbarProps {
  onMenuClick: () => void;
  onSearchChange?: (query: string) => void;
  userName?: string;
  planTier?: string;
}

export function DashboardTopbar({ onMenuClick, onSearchChange, userName: remoteUserName, planTier }: DashboardTopbarProps) {
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
    <header className="sticky top-0 z-20 w-full flex flex-col gap-4 bg-white p-4 shadow-sm border-b border-slate-200 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3">
          <button onClick={onMenuClick} className="md:hidden p-2 -ml-2" aria-label="Open sidebar">
            <Menu size={20} />
          </button>
          <SearchForm onSearchChange={onSearchChange} />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="inline-flex h-12 w-12 items-center justify-center rounded-3xl border border-slate-200 bg-white text-slate-700 shadow-sm hover:bg-blue-50 transition" type="button" aria-label="Notifications">
          <Bell size={18} />
        </button>
        <div className="inline-flex items-center gap-3 rounded-3xl bg-slate-950 px-4 py-3 text-white shadow-sm">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-600 font-semibold">{userInitial}</span>
          <div className="text-sm">
            <strong className="block max-w-40 truncate">{userName}</strong>
            {planLabel && <small className="block max-w-40 truncate text-slate-300">{planLabel}</small>}
          </div>
        </div>
      </div>
    </header>
  );
}

function SearchForm({ onSearchChange }: { onSearchChange?: (query: string) => void }) {
  const [query, setQuery] = useState("");

  const handleFormSubmit = (e: FormEvent<HTMLFormElement>) => {
    // Prevent page reload on form submission
    e.preventDefault();
    // Trigger the search on the parent page
    onSearchChange?.(query);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    onSearchChange?.(newQuery);
  };

  return (
    <form onSubmit={handleFormSubmit} className="w-full">
      <label className="flex items-center gap-3 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 w-full text-slate-700 focus-within:ring-2 focus-within:ring-blue-200">
        <Search size={18} aria-hidden="true" className="text-blue-700" />
        <input id="dashboard-search" type="search" placeholder="Search on this page..." className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400" value={query} onChange={handleInputChange} />
      </label>
    </form>
  );
}
