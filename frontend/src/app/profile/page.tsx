"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

function TagList({ items }: { items: string[] }) {
  if (!items.length) return <p className="text-sm text-black/40 dark:text-white/40">None extracted</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span key={item} className="rounded-full bg-black/5 px-2.5 py-1 text-xs dark:bg-white/10">
          {item}
        </span>
      ))}
    </div>
  );
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getProfile().then(setProfile);
  }, []);

  async function handleSave() {
    if (!profile) return;
    setSaving(true);
    try {
      const updated = await api.updateProfile(profile);
      setProfile(updated);
    } finally {
      setSaving(false);
    }
  }

  if (!profile) return <p className="text-sm text-black/60 dark:text-white/60">Loading...</p>;

  const field = (label: string, key: keyof Profile) => (
    <div>
      <label className="text-xs font-medium text-black/60 dark:text-white/60">{label}</label>
      <input
        className="mt-1 w-full rounded-md border border-black/15 bg-transparent px-3 py-2 text-sm dark:border-white/15"
        value={(profile[key] as string) || ""}
        onChange={(e) => setProfile({ ...profile, [key]: e.target.value })}
      />
    </div>
  );

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Profile</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-black px-4 py-2 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        {field("Name", "name")}
        {field("Email", "email")}
        {field("Phone", "phone")}
        {field("LinkedIn", "linkedin")}
        {field("Portfolio", "portfolio")}
        <div>
          <label className="text-xs font-medium text-black/60 dark:text-white/60">Total Experience (years)</label>
          <input
            type="number"
            className="mt-1 w-full rounded-md border border-black/15 bg-transparent px-3 py-2 text-sm dark:border-white/15"
            value={profile.total_experience_years ?? ""}
            onChange={(e) =>
              setProfile({ ...profile, total_experience_years: e.target.value ? Number(e.target.value) : null })
            }
          />
        </div>
      </div>

      <div className="mt-8 space-y-6">
        <div>
          <h2 className="mb-2 text-sm font-medium">Skills</h2>
          <TagList items={profile.skills} />
        </div>
        <div>
          <h2 className="mb-2 text-sm font-medium">Technologies</h2>
          <TagList items={profile.technologies} />
        </div>
        <div>
          <h2 className="mb-2 text-sm font-medium">Certifications</h2>
          <TagList items={profile.certifications} />
        </div>
        <div>
          <h2 className="mb-2 text-sm font-medium">Domain Expertise</h2>
          <TagList items={profile.domain_expertise} />
        </div>
        {profile.experience.length > 0 && (
          <div>
            <h2 className="mb-2 text-sm font-medium">Experience</h2>
            <ul className="space-y-2">
              {profile.experience.map((exp, i) => (
                <li key={i} className="rounded-md border border-black/10 p-3 text-sm dark:border-white/10">
                  <pre className="whitespace-pre-wrap font-sans">{JSON.stringify(exp, null, 2)}</pre>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
