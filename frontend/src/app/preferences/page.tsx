"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Preferences } from "@/lib/types";

function ListInput({
  label,
  values,
  onChange,
}: {
  label: string;
  values: string[];
  onChange: (values: string[]) => void;
}) {
  const [text, setText] = useState(values.join(", "));
  const [syncedValues, setSyncedValues] = useState(values);

  // Adjust local edit buffer when the prop changes from outside (e.g. after a save),
  // without discarding in-progress typing on every parent re-render.
  if (values !== syncedValues) {
    setSyncedValues(values);
    setText(values.join(", "));
  }

  return (
    <div>
      <label className="text-xs font-medium text-black/60 dark:text-white/60">{label}</label>
      <input
        className="mt-1 w-full rounded-md border border-black/15 bg-transparent px-3 py-2 text-sm dark:border-white/15"
        value={text}
        placeholder="Comma-separated"
        onChange={(e) => setText(e.target.value)}
        onBlur={() =>
          onChange(
            text
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean)
          )
        }
      />
    </div>
  );
}

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getPreferences().then(setPrefs);
  }, []);

  async function handleSave() {
    if (!prefs) return;
    setSaving(true);
    try {
      const updated = await api.updatePreferences(prefs);
      setPrefs(updated);
    } finally {
      setSaving(false);
    }
  }

  if (!prefs) return <p className="text-sm text-black/60 dark:text-white/60">Loading...</p>;

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Preferences</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-black px-4 py-2 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>

      <div className="mt-6 space-y-4">
        <ListInput label="Preferred Titles" values={prefs.preferred_titles} onChange={(v) => setPrefs({ ...prefs, preferred_titles: v })} />
        <ListInput label="Preferred Locations" values={prefs.preferred_locations} onChange={(v) => setPrefs({ ...prefs, preferred_locations: v })} />
        <ListInput label="Countries" values={prefs.countries} onChange={(v) => setPrefs({ ...prefs, countries: v })} />
        <ListInput label="Industries" values={prefs.industries} onChange={(v) => setPrefs({ ...prefs, industries: v })} />
        <ListInput label="Company Size" values={prefs.company_size} onChange={(v) => setPrefs({ ...prefs, company_size: v })} />
        <ListInput label="Employment Type" values={prefs.employment_type} onChange={(v) => setPrefs({ ...prefs, employment_type: v })} />
        <ListInput label="Seniority" values={prefs.seniority} onChange={(v) => setPrefs({ ...prefs, seniority: v })} />

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-black/60 dark:text-white/60">Min Salary</label>
            <input
              type="number"
              className="mt-1 w-full rounded-md border border-black/15 bg-transparent px-3 py-2 text-sm dark:border-white/15"
              value={prefs.min_salary ?? ""}
              onChange={(e) => setPrefs({ ...prefs, min_salary: e.target.value ? Number(e.target.value) : null })}
            />
          </div>
          <div>
            <label className="text-xs font-medium text-black/60 dark:text-white/60">Max Salary</label>
            <input
              type="number"
              className="mt-1 w-full rounded-md border border-black/15 bg-transparent px-3 py-2 text-sm dark:border-white/15"
              value={prefs.max_salary ?? ""}
              onChange={(e) => setPrefs({ ...prefs, max_salary: e.target.value ? Number(e.target.value) : null })}
            />
          </div>
        </div>

        <div className="flex gap-6 pt-2">
          {(["remote_only", "hybrid_ok", "onsite_ok"] as const).map((key) => (
            <label key={key} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={prefs[key]}
                onChange={(e) => setPrefs({ ...prefs, [key]: e.target.checked })}
              />
              {key.replace("_", " ")}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
