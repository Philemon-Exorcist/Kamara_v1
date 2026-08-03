import { Crown, ShieldAlert, ArrowLeft } from "lucide-react";
import { useMemo } from "react";
import { useLocation } from "react-router";

export function meta() {
  return [
    { title: "Upgrade | Kamara AI" },
    {
      name: "description",
      content: "Upgrade your Kamara AI plan to unlock advanced features.",
    },
  ];
}

export default function UpgradePage() {
  const location = useLocation();

  const details = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return {
      feature: params.get("feature") ?? "this feature",
      reason: params.get("reason") ?? "plan_limit",
      plan: params.get("plan") ?? "pro",
    };
  }, [location.search]);

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-3xl items-center">
        <section className="w-full overflow-hidden rounded-3xl border border-white/10 bg-white/8 p-6 shadow-2xl shadow-slate-950/40 backdrop-blur md:p-10">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-amber-400/15 px-4 py-2 text-sm font-semibold text-amber-200">
            <ShieldAlert size={16} />
            Upgrade required
          </div>

          <h1 className="max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl">
            You’ve reached the limit for {details.feature.replace(/_/g, " ")}.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            Your current plan cannot continue with this action. The reason was <span className="font-semibold text-white">{details.reason}</span>. Upgrade to <span className="font-semibold text-white capitalize">{details.plan}</span> to keep going without interruption.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
              <p className="text-sm font-semibold text-amber-200">What you unlock</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-300">
                <li>Higher message limits</li>
                <li>Larger notes and PDF handling</li>
                <li>External sources and richer study workflows</li>
              </ul>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-5">
              <p className="text-sm font-semibold text-amber-200">Next step</p>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Return to your dashboard after upgrading and the locked feature will become available automatically.
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
            >
              <ArrowLeft size={16} />
              Back to dashboard
            </a>
            <a
              href="/signup"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-amber-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-amber-300"
            >
              <Crown size={16} />
              Upgrade to Pro
            </a>
          </div>
        </section>
      </div>
    </main>
  );
}

