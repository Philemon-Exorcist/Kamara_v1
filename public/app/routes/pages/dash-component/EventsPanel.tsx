import { ClipboardCheck, FileUp, MessageCircle } from "lucide-react";

type Activity = {
  id: string;
  type: string;
  title: string;
  timestamp: string;
};

function getActivityIcon(type: string) {
  if (type === "upload") {
    return <FileUp size={18} />;
  }

  if (type === "exam") {
    return <ClipboardCheck size={18} />;
  }

  return <MessageCircle size={18} />;
}

export function EventsPanel({ activities = [] }: { activities?: Activity[] }) {
  const visibleActivities = activities.slice(0, 3);

  return (
    <section className="rounded-4xl bg-white p-6 shadow-sm border border-slate-200" aria-labelledby="events-title">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 id="events-title" className="text-lg font-semibold text-slate-900">Recent activity</h2>
          <p className="text-sm text-slate-500">Latest learning actions from your account.</p>
        </div>
        <a href="#activity-details" className="text-sm font-semibold text-blue-700 hover:text-blue-800">
          View all
        </a>
      </div>

      <div className="mt-6 space-y-4">
        {visibleActivities.length > 0 ? (
          visibleActivities.map((activity) => (
            <article key={activity.id} className="flex gap-4 rounded-[1.75rem] border border-slate-200 bg-blue-50 p-4">
              <span className="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white text-blue-700 shadow-sm">
                {getActivityIcon(activity.type)}
              </span>
              <div>
                <h3 className="text-base font-semibold text-slate-900">{activity.title}</h3>
                <p className="mt-2 text-sm text-slate-500">{activity.timestamp}</p>
              </div>
            </article>
          ))
        ) : (
          <article className="rounded-[1.75rem] border border-slate-200 bg-blue-50 p-4">
            <h3 className="text-base font-semibold text-slate-900">No recent activity yet</h3>
            <p className="mt-2 text-sm text-slate-500">Your chats, uploads, and quizzes will show up here.</p>
          </article>
        )}
      </div>
    </section>
  );
}
