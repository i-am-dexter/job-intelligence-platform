"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { ATSResult, GapResult, RankedJob, TailoringResult } from "@/lib/types";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-6 rounded-lg border border-black/10 p-4 dark:border-white/10">
      <h2 className="mb-3 text-sm font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function Pills({ items, tone }: { items: string[]; tone: "positive" | "negative" }) {
  if (!items.length) return <p className="text-sm text-black/40 dark:text-white/40">None</p>;
  const cls =
    tone === "positive"
      ? "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300"
      : "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span key={item} className={`rounded-full px-2.5 py-1 text-xs ${cls}`}>
          {item}
        </span>
      ))}
    </div>
  );
}

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<RankedJob | null>(null);
  const [ats, setAts] = useState<ATSResult | null>(null);
  const [gaps, setGaps] = useState<GapResult | null>(null);
  const [tailoring, setTailoring] = useState<TailoringResult | null>(null);
  const [generating, setGenerating] = useState(false);
  const [saved, setSaved] = useState(false);
  const [applyState, setApplyState] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    api.getJob(params.id).then(setJob);
    api.getAts(params.id).then(setAts).catch(() => {});
    api.getGaps(params.id).then(setGaps).catch(() => {});
    api.getTailoring(params.id).then(setTailoring).catch(() => {});
  }, [params.id]);

  async function handleGenerateTailoring() {
    setGenerating(true);
    try {
      setTailoring(await api.generateTailoring(params.id));
    } finally {
      setGenerating(false);
    }
  }

  async function handleToggleSave() {
    if (saved) {
      await api.unsaveJob(params.id);
      setSaved(false);
    } else {
      await api.saveJob(params.id);
      setSaved(true);
    }
  }

  async function handleApply() {
    await api.createApplication(params.id, "Applied");
    setApplyState("Marked as Applied");
    if (job) window.open(job.url, "_blank");
  }

  if (!job) return <p className="text-sm text-black/60 dark:text-white/60">Loading...</p>;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{job.title}</h1>
          <p className="mt-1 text-black/60 dark:text-white/60">
            {job.company_name} · {job.location || (job.remote ? "Remote" : "N/A")} · via {job.source}
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleToggleSave} className="rounded-md border border-black/15 px-4 py-2 text-sm dark:border-white/15">
            {saved ? "Saved" : "Save"}
          </button>
          <button onClick={handleApply} className="rounded-md bg-black px-4 py-2 text-sm text-white dark:bg-white dark:text-black">
            Apply
          </button>
        </div>
      </div>
      {applyState && <p className="mt-2 text-sm text-green-700 dark:text-green-400">{applyState}</p>}

      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <span>Match: <strong>{job.match_score.toFixed(0)}</strong></span>
        <span>Final Score: <strong>{job.final_score.toFixed(0)}</strong></span>
        {(job.salary_min || job.salary_max) && (
          <span>
            {job.currency || "USD"} {job.salary_min?.toLocaleString()}
            {job.salary_max ? ` - ${job.salary_max.toLocaleString()}` : ""}
          </span>
        )}
      </div>

      <Section title="Description">
        <p className="whitespace-pre-wrap text-sm text-black/80 dark:text-white/80">{job.description || "No description available."}</p>
      </Section>

      {ats && (
        <Section title={`ATS Analysis — ${ats.ats_score.toFixed(0)}% keyword coverage`}>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Matched keywords</p>
              <Pills items={ats.matched_keywords} tone="positive" />
            </div>
            <div>
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Missing keywords</p>
              <Pills items={ats.missing_keywords} tone="negative" />
            </div>
          </div>
          <ul className="mt-3 list-disc pl-5 text-sm text-black/70 dark:text-white/70">
            {ats.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </Section>
      )}

      {gaps && (
        <Section title="Skill Gap Analysis">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Matched skills</p>
              <Pills items={gaps.matched_skills} tone="positive" />
            </div>
            <div>
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Missing skills</p>
              <Pills items={gaps.missing_skills} tone="negative" />
            </div>
          </div>
          {gaps.recommended_certifications.length > 0 && (
            <div className="mt-3">
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Recommended certifications</p>
              <ul className="list-disc pl-5 text-sm">
                {gaps.recommended_certifications.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          )}
          {gaps.recommended_projects.length > 0 && (
            <div className="mt-3">
              <p className="mb-1 text-xs font-medium text-black/60 dark:text-white/60">Recommended projects</p>
              <ul className="list-disc pl-5 text-sm">
                {gaps.recommended_projects.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      )}

      <Section title="Resume Tailoring">
        {tailoring ? (
          <div className="space-y-3 text-sm">
            <p><span className="font-medium">Summary: </span>{tailoring.tailored_summary}</p>
            {tailoring.tailored_bullets.length > 0 && (
              <div>
                <p className="mb-1 font-medium">Suggested bullets</p>
                <ul className="list-disc pl-5">
                  {tailoring.tailored_bullets.map((b, i) => (
                    <li key={i}>{b}</li>
                  ))}
                </ul>
              </div>
            )}
            {tailoring.resume_improvements.length > 0 && (
              <div>
                <p className="mb-1 font-medium">Improvements</p>
                <ul className="list-disc pl-5">
                  {tailoring.resume_improvements.map((imp, i) => (
                    <li key={i}>{imp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-black/50 dark:text-white/50">No suggestions generated yet.</p>
        )}
        <button
          onClick={handleGenerateTailoring}
          disabled={generating}
          className="mt-3 rounded-md border border-black/15 px-4 py-1.5 text-sm disabled:opacity-50 dark:border-white/15"
        >
          {generating ? "Generating..." : tailoring ? "Regenerate suggestions" : "Generate suggestions"}
        </button>
      </Section>

      <div className="mt-6">
        <a href={job.url} target="_blank" rel="noreferrer" className="text-sm underline">
          Open original job posting →
        </a>
      </div>
    </div>
  );
}
