"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { JobFilters, RankedJob } from "@/lib/types";

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 75
      ? "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300"
      : score >= 50
        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300"
        : "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
  return <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${color}`}>{score.toFixed(0)}</span>;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<RankedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [aggregating, setAggregating] = useState(false);
  const [filters, setFilters] = useState<JobFilters>({});

  async function load(currentFilters: JobFilters) {
    setLoading(true);
    try {
      setJobs(await api.listJobs(currentFilters));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      try {
        const result = await api.listJobs({});
        if (!ignore) setJobs(result);
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => {
      ignore = true;
    };
  }, []);

  async function handleAggregate() {
    setAggregating(true);
    try {
      await api.aggregateJobs();
      await load(filters);
    } finally {
      setAggregating(false);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Jobs</h1>
        <button
          onClick={handleAggregate}
          disabled={aggregating}
          className="rounded-md border border-black/15 px-4 py-2 text-sm disabled:opacity-50 dark:border-white/15"
        >
          {aggregating ? "Fetching jobs..." : "Fetch new jobs"}
        </button>
      </div>

      <form
        className="mt-4 flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          load(filters);
        }}
      >
        <input
          placeholder="Keyword"
          className="rounded-md border border-black/15 bg-transparent px-3 py-1.5 text-sm dark:border-white/15"
          value={filters.keyword || ""}
          onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
        />
        <input
          placeholder="Location"
          className="rounded-md border border-black/15 bg-transparent px-3 py-1.5 text-sm dark:border-white/15"
          value={filters.location || ""}
          onChange={(e) => setFilters({ ...filters, location: e.target.value })}
        />
        <input
          placeholder="Company"
          className="rounded-md border border-black/15 bg-transparent px-3 py-1.5 text-sm dark:border-white/15"
          value={filters.company || ""}
          onChange={(e) => setFilters({ ...filters, company: e.target.value })}
        />
        <select
          className="rounded-md border border-black/15 bg-transparent px-3 py-1.5 text-sm dark:border-white/15"
          value={filters.source || ""}
          onChange={(e) => setFilters({ ...filters, source: e.target.value || undefined })}
        >
          <option value="">All sources</option>
          <option value="greenhouse">Greenhouse</option>
          <option value="lever">Lever</option>
          <option value="ashby">Ashby</option>
          <option value="smartrecruiters">SmartRecruiters</option>
          <option value="workable">Workable</option>
        </select>
        <label className="flex items-center gap-1.5 text-sm">
          <input
            type="checkbox"
            checked={!!filters.remote}
            onChange={(e) => setFilters({ ...filters, remote: e.target.checked || undefined })}
          />
          Remote only
        </label>
        <button type="submit" className="rounded-md bg-black px-4 py-1.5 text-sm text-white dark:bg-white dark:text-black">
          Filter
        </button>
      </form>

      {loading ? (
        <p className="mt-6 text-sm text-black/60 dark:text-white/60">Loading...</p>
      ) : jobs.length === 0 ? (
        <p className="mt-6 text-sm text-black/60 dark:text-white/60">
          No jobs yet. Click &quot;Fetch new jobs&quot; to aggregate from configured sources.
        </p>
      ) : (
        <ul className="mt-6 divide-y divide-black/10 dark:divide-white/10">
          {jobs.map((job) => (
            <li key={job.id} className="py-4">
              <Link href={`/jobs/${job.id}`} className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-medium">{job.title}</p>
                  <p className="text-sm text-black/60 dark:text-white/60">
                    {job.company_name} · {job.location || (job.remote ? "Remote" : "N/A")} · {job.source}
                  </p>
                  {(job.salary_min || job.salary_max) && (
                    <p className="mt-1 text-xs text-black/50 dark:text-white/50">
                      {job.currency || "USD"} {job.salary_min?.toLocaleString()}
                      {job.salary_max ? ` - ${job.salary_max.toLocaleString()}` : ""}
                    </p>
                  )}
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                  <ScoreBadge score={job.match_score} />
                  <span className="text-xs text-black/40 dark:text-white/40">final {job.final_score.toFixed(0)}</span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
