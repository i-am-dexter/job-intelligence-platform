"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AnalyticsSummary, DashboardMetrics } from "@/lib/types";

function StatTile({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-black/10 p-4 dark:border-white/10">
      <p className="text-xs text-black/60 dark:text-white/60">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);

  useEffect(() => {
    api.getDashboardMetrics().then(setMetrics);
    api.getAnalytics().then(setAnalytics);
  }, []);

  if (!metrics) return <p className="text-sm text-black/60 dark:text-white/60">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StatTile label="Total Jobs" value={metrics.total_jobs} />
        <StatTile label="Strong Matches" value={metrics.strong_matches} />
        <StatTile label="Medium Matches" value={metrics.medium_matches} />
        <StatTile label="Weak Matches" value={metrics.weak_matches} />
        <StatTile label="Saved Jobs" value={metrics.saved_jobs} />
        <StatTile label="Applications" value={metrics.applications} />
        <StatTile label="Interviews" value={metrics.interviews} />
        <StatTile label="Offers" value={metrics.offers} />
        <StatTile label="Companies" value={metrics.companies} />
        <StatTile label="Sources" value={metrics.sources} />
      </div>

      {analytics && (
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-black/10 p-4 dark:border-white/10">
            <h2 className="mb-3 text-sm font-semibold">Application Funnel</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Interview rate</span><strong>{analytics.interview_rate}%</strong></div>
              <div className="flex justify-between"><span>Offer rate</span><strong>{analytics.offer_rate}%</strong></div>
              <div className="flex justify-between"><span>Success rate</span><strong>{analytics.application_success_rate}%</strong></div>
            </div>
          </div>

          <div className="rounded-lg border border-black/10 p-4 dark:border-white/10">
            <h2 className="mb-3 text-sm font-semibold">Source Effectiveness</h2>
            {Object.keys(analytics.source_effectiveness).length === 0 ? (
              <p className="text-sm text-black/40 dark:text-white/40">No application data yet</p>
            ) : (
              <div className="space-y-2 text-sm">
                {Object.entries(analytics.source_effectiveness).map(([source, rate]) => (
                  <div key={source} className="flex items-center gap-2">
                    <span className="w-28 shrink-0 capitalize">{source}</span>
                    <div className="h-2 flex-1 rounded-full bg-black/10 dark:bg-white/10">
                      <div className="h-2 rounded-full bg-black dark:bg-white" style={{ width: `${Math.min(rate, 100)}%` }} />
                    </div>
                    <span className="w-10 text-right">{rate}%</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border border-black/10 p-4 dark:border-white/10 md:col-span-2">
            <h2 className="mb-3 text-sm font-semibold">Top Paying Roles</h2>
            {analytics.top_paying_roles.length === 0 ? (
              <p className="text-sm text-black/40 dark:text-white/40">No salary data yet</p>
            ) : (
              <ul className="divide-y divide-black/10 text-sm dark:divide-white/10">
                {analytics.top_paying_roles.map((role, i) => (
                  <li key={i} className="flex justify-between py-1.5">
                    <span>{role.title} · {role.company}</span>
                    <span className="font-medium">{role.currency || "USD"} {role.salary_max.toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
