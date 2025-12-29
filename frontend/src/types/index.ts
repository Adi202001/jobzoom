// User Profile Types
export interface Personal {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
}

export interface JobPreferences {
  target_titles: string[];
  locations: string[];
  remote_preference: 'remote_only' | 'hybrid_ok' | 'onsite_ok' | 'any';
  salary_min: number | null;
  salary_max: number | null;
  job_types: string[];
}

export interface Filters {
  required_keywords: string[];
  excluded_keywords: string[];
  blacklisted_companies: string[];
}

export interface Experience {
  company: string;
  title: string;
  duration: string;
  bullets: string[];
}

export interface Education {
  institution: string;
  degree: string;
  year: string;
}

export interface Skills {
  technical: string[];
  tools: string[];
  soft: string[];
}

export interface ParsedResume {
  summary: string;
  experience: Experience[];
  education: Education[];
  skills: Skills;
  certifications: string[];
  projects: { name: string; description: string; tech: string[] }[];
  extracted_keywords: string[];
}

export interface Resume {
  raw_text: string;
  parsed: ParsedResume | null;
  file_path: string;
}

export interface UserProfile {
  user_id: string;
  personal: Personal;
  job_preferences: JobPreferences;
  filters: Filters;
  resume: Resume;
}

// Job Types
export interface SalaryRange {
  min: number | null;
  max: number | null;
}

export interface Job {
  job_id: string;
  title: string;
  company: string;
  location: string;
  remote_status: 'remote' | 'hybrid' | 'onsite';
  salary_range: SalaryRange;
  job_type: string;
  posted_date: string | null;
  description: string;
  requirements: string[];
  responsibilities: string[];
  application_url: string;
  source_url: string;
  scraped_at: string;
  status: 'new' | 'matched' | 'applied' | 'rejected' | 'expired';
}

export interface JobMatch extends Job {
  match_score: number;
  highlights: string[];
}

// Application Types
export interface TimelineEntry {
  status: string;
  date: string;
  note: string;
}

export interface Application {
  app_id: string;
  job_id: string;
  user_id: string;
  status: 'preparing' | 'ready' | 'submitted' | 'interview' | 'offer' | 'rejected';
  match_score: number;
  tailored_resume: string;
  cover_letter: string;
  form_answers: Record<string, string>;
  submitted_at: string | null;
  timeline: TimelineEntry[];
  job?: Job;
}

// Stats Types
export interface DashboardStats {
  total_applications: number;
  by_status: Record<string, number>;
  response_rate: number;
  interviews_scheduled: number;
  new_matches: number;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}
