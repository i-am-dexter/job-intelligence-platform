import type {
  ATSResult,
  Application,
  ApplicationStatus,
  AnalyticsSummary,
  DashboardMetrics,
  GapResult,
  JobFilters,
  Preferences,
  Profile,
  RankedJob,
  ResumeVersion,
  TailoringResult,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: init?.body instanceof FormData ? init?.headers : { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  getProfile: () => request<Profile>("/profile"),
  updateProfile: (data: Partial<Profile>) =>
    request<Profile>("/profile", { method: "PUT", body: JSON.stringify(data) }),

  getPreferences: () => request<Preferences>("/preferences"),
  updatePreferences: (data: Partial<Preferences>) =>
    request<Preferences>("/preferences", { method: "PUT", body: JSON.stringify(data) }),

  uploadResume: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{ resume_version: ResumeVersion; profile: Profile }>("/resume/upload", {
      method: "POST",
      body: formData,
    });
  },
  listResumeVersions: () => request<ResumeVersion[]>("/resume/versions"),

  listJobs: (filters: JobFilters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") params.set(key, String(value));
    });
    return request<RankedJob[]>(`/jobs?${params.toString()}`);
  },
  getJob: (id: string) => request<RankedJob>(`/jobs/${id}`),
  aggregateJobs: () => request<{ stored_by_source: Record<string, number>; total_stored: number }>("/jobs/aggregate", { method: "POST" }),
  saveJob: (id: string) => request<{ saved: boolean }>(`/jobs/${id}/save`, { method: "POST" }),
  unsaveJob: (id: string) => request<{ saved: boolean }>(`/jobs/${id}/save`, { method: "DELETE" }),
  listSavedJobs: () => request<RankedJob[]>("/jobs/saved/list"),

  getAts: (jobId: string) => request<ATSResult>(`/jobs/${jobId}/ats`),
  getGaps: (jobId: string) => request<GapResult>(`/jobs/${jobId}/gaps`),
  getTailoring: (jobId: string) => request<TailoringResult | null>(`/jobs/${jobId}/tailoring`),
  generateTailoring: (jobId: string) => request<TailoringResult>(`/jobs/${jobId}/tailoring`, { method: "POST" }),

  listApplications: (status?: ApplicationStatus) =>
    request<Application[]>(`/applications${status ? `?status=${status}` : ""}`),
  createApplication: (jobId: string, status: ApplicationStatus = "Saved", notes?: string) =>
    request<Application>("/applications", { method: "POST", body: JSON.stringify({ job_id: jobId, status, notes }) }),
  updateApplication: (id: string, data: { status?: ApplicationStatus; notes?: string }) =>
    request<Application>(`/applications/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteApplication: (id: string) => request<{ deleted: boolean }>(`/applications/${id}`, { method: "DELETE" }),

  getDashboardMetrics: () => request<DashboardMetrics>("/dashboard/metrics"),
  getAnalytics: () => request<AnalyticsSummary>("/dashboard/analytics"),
};

export { ApiError };
