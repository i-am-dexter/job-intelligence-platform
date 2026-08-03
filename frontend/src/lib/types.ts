export interface Profile {
  id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  portfolio: string | null;
  experience: Array<Record<string, unknown>>;
  education: Array<Record<string, unknown>>;
  skills: string[];
  certifications: string[];
  projects: Array<Record<string, unknown>>;
  technologies: string[];
  domain_expertise: string[];
  preferred_roles: string[];
  preferred_locations: string[];
  total_experience_years: number | null;
  created_at: string;
  updated_at: string;
}

export interface Preferences {
  id: string;
  preferred_titles: string[];
  preferred_locations: string[];
  remote_only: boolean;
  hybrid_ok: boolean;
  onsite_ok: boolean;
  countries: string[];
  min_salary: number | null;
  max_salary: number | null;
  salary_currency: string;
  employment_type: string[];
  seniority: string[];
  industries: string[];
  company_size: string[];
  created_at: string;
  updated_at: string;
}

export interface JobSkill {
  skill: string;
  kind: "required" | "preferred";
}

export interface Job {
  id: string;
  company_name: string;
  title: string;
  description: string | null;
  requirements: string | null;
  location: string | null;
  country: string | null;
  remote: boolean;
  salary_min: number | null;
  salary_max: number | null;
  currency: string | null;
  salary_confidence: string | null;
  employment_type: string | null;
  experience_required: string | null;
  source: string;
  url: string;
  posted_date: string | null;
  created_at: string;
  skills: JobSkill[];
}

export interface RankedJob extends Job {
  match_score: number;
  salary_score: number;
  company_score: number;
  remote_bonus: number;
  preference_bonus: number;
  final_score: number;
}

export interface JobFilters {
  keyword?: string;
  source?: string;
  company?: string;
  location?: string;
  country?: string;
  min_salary?: number;
  remote?: boolean;
  min_score?: number;
  employment_type?: string;
}

export interface ATSResult {
  ats_score: number;
  keyword_coverage: number;
  matched_keywords: string[];
  missing_keywords: string[];
  recommendations: string[];
}

export interface GapResult {
  matched_skills: string[];
  missing_skills: string[];
  suggested_skills: string[];
  learning_priorities: string[];
  recommended_certifications: string[];
  recommended_projects: string[];
}

export interface TailoringResult {
  tailored_summary: string;
  tailored_bullets: string[];
  keyword_suggestions: string[];
  project_recommendations: string[];
  resume_improvements: string[];
}

export type ApplicationStatus = "Saved" | "Applied" | "Interviewing" | "Offer" | "Rejected" | "Archived";

export interface Application {
  id: string;
  job_id: string;
  status: ApplicationStatus;
  notes: string | null;
  timeline: Array<{ status: string; at: string }>;
  created_at: string;
  updated_at: string;
  job: Job | null;
}

export interface DashboardMetrics {
  total_jobs: number;
  strong_matches: number;
  medium_matches: number;
  weak_matches: number;
  applications: number;
  interviews: number;
  offers: number;
  saved_jobs: number;
  companies: number;
  sources: number;
}

export interface AnalyticsSummary {
  application_success_rate: number;
  interview_rate: number;
  offer_rate: number;
  source_effectiveness: Record<string, number>;
  top_matching_domains: string[];
  top_paying_roles: Array<{ title: string; company: string; salary_max: number; currency: string | null }>;
}

export interface ResumeVersion {
  id: string;
  filename: string;
  uploaded_at: string;
}
