"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { ResumeVersion } from "@/lib/types";

export default function ResumePage() {
  const router = useRouter();
  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    api.listResumeVersions().then(setVersions).catch(() => {});
  }, []);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await api.uploadResume(file);
      setSuccess(`Parsed "${result.resume_version.filename}" and updated your profile.`);
      setVersions((prev) => [result.resume_version, ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold">Upload Resume</h1>
      <p className="mt-1 text-sm text-black/60 dark:text-white/60">
        PDF or DOCX. Your profile will be extracted and updated automatically.
      </p>

      <label className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-black/20 p-10 text-center hover:border-black/40 dark:border-white/20 dark:hover:border-white/40">
        <span className="text-sm font-medium">{uploading ? "Parsing resume..." : "Click to select a resume file"}</span>
        <span className="mt-1 text-xs text-black/50 dark:text-white/50">.pdf or .docx</span>
        <input type="file" accept=".pdf,.docx" className="hidden" disabled={uploading} onChange={handleFileChange} />
      </label>

      {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">{error}</p>}
      {success && (
        <div className="mt-4 rounded-md bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950 dark:text-green-300">
          {success}{" "}
          <button className="underline" onClick={() => router.push("/profile")}>
            View profile
          </button>
        </div>
      )}

      {versions.length > 0 && (
        <div className="mt-8">
          <h2 className="text-sm font-medium text-black/60 dark:text-white/60">Upload history</h2>
          <ul className="mt-2 divide-y divide-black/10 dark:divide-white/10">
            {versions.map((v) => (
              <li key={v.id} className="flex items-center justify-between py-2 text-sm">
                <span>{v.filename}</span>
                <span className="text-black/50 dark:text-white/50">{new Date(v.uploaded_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
