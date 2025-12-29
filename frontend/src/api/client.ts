import axios from 'axios';
import type { UserProfile, Job, JobMatch, Application, DashboardStats } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Profile APIs
export const profileApi = {
  create: async (data: {
    name: string;
    email: string;
    phone?: string;
    location?: string;
    linkedin?: string;
    target_titles?: string[];
    locations?: string[];
    remote_preference?: string;
    salary_min?: number;
    salary_max?: number;
  }) => {
    const response = await api.post<{ user_id: string }>('/profile', data);
    return response.data;
  },

  get: async (userId: string) => {
    const response = await api.get<UserProfile>(`/profile/${userId}`);
    return response.data;
  },

  update: async (userId: string, data: Partial<UserProfile>) => {
    const response = await api.put<UserProfile>(`/profile/${userId}`, data);
    return response.data;
  },

  updatePreferences: async (userId: string, preferences: Partial<UserProfile['job_preferences']>) => {
    const response = await api.put(`/profile/${userId}/preferences`, preferences);
    return response.data;
  },

  updateFilters: async (userId: string, filters: Partial<UserProfile['filters']>) => {
    const response = await api.put(`/profile/${userId}/filters`, filters);
    return response.data;
  },
};

// Resume APIs
export const resumeApi = {
  upload: async (userId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/resume/${userId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  parse: async (userId: string, text?: string) => {
    const response = await api.post(`/resume/${userId}/parse`, { text });
    return response.data;
  },
};

// Job APIs
export const jobApi = {
  scrape: async (url: string, userId?: string) => {
    const response = await api.post<{ jobs_found: number; job_ids: string[] }>('/jobs/scrape', {
      url,
      user_id: userId,
    });
    return response.data;
  },

  list: async (status?: string, limit?: number) => {
    const response = await api.get<Job[]>('/jobs', {
      params: { status, limit },
    });
    return response.data;
  },

  get: async (jobId: string) => {
    const response = await api.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },

  match: async (userId: string, jobId?: string) => {
    const response = await api.post<{ matches: JobMatch[] }>('/jobs/match', {
      user_id: userId,
      job_id: jobId,
    });
    return response.data;
  },

  getRecommendations: async (userId: string, minScore = 70, limit = 20) => {
    const response = await api.get<JobMatch[]>(`/jobs/recommendations/${userId}`, {
      params: { min_score: minScore, limit },
    });
    return response.data;
  },
};

// Application APIs
export const applicationApi = {
  create: async (userId: string, jobId: string) => {
    const response = await api.post<Application>('/applications', {
      user_id: userId,
      job_id: jobId,
    });
    return response.data;
  },

  prepare: async (userId: string, jobId: string) => {
    const response = await api.post<{
      tailored_resume: string;
      cover_letter: string;
    }>(`/applications/prepare`, {
      user_id: userId,
      job_id: jobId,
    });
    return response.data;
  },

  list: async (userId: string, status?: string) => {
    const response = await api.get<Application[]>(`/applications/user/${userId}`, {
      params: { status },
    });
    return response.data;
  },

  get: async (appId: string) => {
    const response = await api.get<Application>(`/applications/${appId}`);
    return response.data;
  },

  updateStatus: async (appId: string, status: string, note?: string) => {
    const response = await api.put(`/applications/${appId}/status`, {
      status,
      note,
    });
    return response.data;
  },

  addNote: async (appId: string, note: string) => {
    const response = await api.post(`/applications/${appId}/note`, { note });
    return response.data;
  },
};

// Digest APIs
export const digestApi = {
  getDaily: async (userId: string) => {
    const response = await api.get<{ digest: string; stats: Record<string, number> }>(
      `/digest/${userId}/daily`
    );
    return response.data;
  },

  getWeekly: async (userId: string) => {
    const response = await api.get(`/digest/${userId}/weekly`);
    return response.data;
  },

  getPipeline: async (userId: string) => {
    const response = await api.get(`/digest/${userId}/pipeline`);
    return response.data;
  },
};

// Dashboard APIs
export const dashboardApi = {
  getStats: async (userId: string) => {
    const response = await api.get<DashboardStats>(`/dashboard/${userId}/stats`);
    return response.data;
  },
};

export default api;
