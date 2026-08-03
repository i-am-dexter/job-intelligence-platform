"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Application, ApplicationStatus } from "@/lib/types";

const STATUSES: ApplicationStatus[] = ["Saved", "Applied", "Interviewing", "Offer", "Rejected", "Archived"];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listApplications()
      .then(setApplications)
      .finally(() => setLoading(false));
  }, []);

  async function handleStatusChange(app: Application, status: ApplicationStatus) {
    const updated = await api.updateApplication(app.id, { status });
    setApplications((prev) => prev.map((a) => (a.id === app.id ? updated : a)));
  }

  async function handleNotesBlur(app: Application, notes: string) {
    if (notes === (app.notes || "")) return;
    const updated = await api.updateApplication(app.id, { notes });
    setApplications((prev) => prev.map((a) => (a.id === app.id ? updated : a)));
  }

  if (loading) return <p className="text-sm text-black/60 dark:text-white/60">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-semibold">Applications</h1>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {STATUSES.map((status) => {
          const items = applications.filter((a) => a.status === status);
          return (
            <div key={status} className="rounded-lg border border-black/10 p-3 dark:border-white/10">
              <h2 className="mb-3 flex items-center justify-between text-sm font-semibold">
                {status}
                <span className="text-xs font-normal text-black/40 dark:text-white/40">{items.length}</span>
              </h2>
              <div className="space-y-3">
                {items.map((app) => (
                  <div key={app.id} className="rounded-md border border-black/10 p-3 text-sm dark:border-white/10">
                    {app.job ? (
                      <Link href={`/jobs/${app.job.id}`} className="font-medium hover:underline">
                        {app.job.title}
                      </Link>
                    ) : (
                      <span className="font-medium">Unknown job</span>
                    )}
                    {app.job && <p className="text-xs text-black/50 dark:text-white/50">{app.job.company_name}</p>}

                    <select
                      className="mt-2 w-full rounded-md border border-black/15 bg-transparent px-2 py-1 text-xs dark:border-white/15"
                      value={app.status}
                      onChange={(e) => handleStatusChange(app, e.target.value as ApplicationStatus)}
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>

                    <textarea
                      className="mt-2 w-full rounded-md border border-black/15 bg-transparent px-2 py-1 text-xs dark:border-white/15"
                      placeholder="Notes"
                      defaultValue={app.notes || ""}
                      rows={2}
                      onBlur={(e) => handleNotesBlur(app, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
