import { useState, useEffect } from 'react';
import { Filter, Download, Loader2 } from 'lucide-react';
import ApplicationCard from '../components/ApplicationCard';
import type { Application } from '../types';

interface ApplicationsProps {
  userId: string;
}

// Mock data
const mockApplications: Application[] = [
  {
    app_id: 'app1',
    job_id: '1',
    user_id: 'user1',
    status: 'interview',
    match_score: 92,
    tailored_resume: 'Tailored resume content...',
    cover_letter: 'Cover letter content...',
    form_answers: {},
    submitted_at: '2024-01-10T10:00:00Z',
    timeline: [
      { status: 'preparing', date: '2024-01-08T10:00:00Z', note: 'Application created' },
      { status: 'submitted', date: '2024-01-10T10:00:00Z', note: 'Application submitted' },
      { status: 'interview', date: '2024-01-15T10:00:00Z', note: 'Interview scheduled for Jan 20' },
    ],
    job: {
      job_id: '1',
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc',
      location: 'San Francisco, CA',
      remote_status: 'hybrid',
      salary_range: { min: 150000, max: 200000 },
      job_type: 'full-time',
      posted_date: '2024-01-05',
      description: '',
      requirements: [],
      responsibilities: [],
      application_url: '',
      source_url: '',
      scraped_at: '',
      status: 'matched',
    },
  },
  {
    app_id: 'app2',
    job_id: '2',
    user_id: 'user1',
    status: 'submitted',
    match_score: 87,
    tailored_resume: 'Tailored resume content...',
    cover_letter: 'Cover letter content...',
    form_answers: {},
    submitted_at: '2024-01-12T10:00:00Z',
    timeline: [
      { status: 'preparing', date: '2024-01-11T10:00:00Z', note: 'Application created' },
      { status: 'submitted', date: '2024-01-12T10:00:00Z', note: 'Application submitted' },
    ],
    job: {
      job_id: '2',
      title: 'Full Stack Developer',
      company: 'StartupXYZ',
      location: 'Remote',
      remote_status: 'remote',
      salary_range: { min: 120000, max: 160000 },
      job_type: 'full-time',
      posted_date: '2024-01-08',
      description: '',
      requirements: [],
      responsibilities: [],
      application_url: '',
      source_url: '',
      scraped_at: '',
      status: 'matched',
    },
  },
  {
    app_id: 'app3',
    job_id: '3',
    user_id: 'user1',
    status: 'offer',
    match_score: 78,
    tailored_resume: 'Tailored resume content...',
    cover_letter: 'Cover letter content...',
    form_answers: {},
    submitted_at: '2024-01-05T10:00:00Z',
    timeline: [
      { status: 'preparing', date: '2024-01-04T10:00:00Z', note: 'Application created' },
      { status: 'submitted', date: '2024-01-05T10:00:00Z', note: 'Application submitted' },
      { status: 'interview', date: '2024-01-10T10:00:00Z', note: 'First interview completed' },
      { status: 'interview', date: '2024-01-14T10:00:00Z', note: 'Final interview completed' },
      { status: 'offer', date: '2024-01-16T10:00:00Z', note: 'Received offer! $165k base + equity' },
    ],
    job: {
      job_id: '3',
      title: 'Backend Engineer',
      company: 'BigTech Corp',
      location: 'New York, NY',
      remote_status: 'hybrid',
      salary_range: { min: 140000, max: 180000 },
      job_type: 'full-time',
      posted_date: '2024-01-01',
      description: '',
      requirements: [],
      responsibilities: [],
      application_url: '',
      source_url: '',
      scraped_at: '',
      status: 'applied',
    },
  },
  {
    app_id: 'app4',
    job_id: '4',
    user_id: 'user1',
    status: 'rejected',
    match_score: 65,
    tailored_resume: '',
    cover_letter: '',
    form_answers: {},
    submitted_at: '2024-01-03T10:00:00Z',
    timeline: [
      { status: 'submitted', date: '2024-01-03T10:00:00Z', note: 'Application submitted' },
      { status: 'rejected', date: '2024-01-08T10:00:00Z', note: 'Position filled' },
    ],
    job: {
      job_id: '4',
      title: 'DevOps Engineer',
      company: 'CloudNine',
      location: 'Austin, TX',
      remote_status: 'onsite',
      salary_range: { min: 130000, max: 170000 },
      job_type: 'full-time',
      posted_date: '2023-12-28',
      description: '',
      requirements: [],
      responsibilities: [],
      application_url: '',
      source_url: '',
      scraped_at: '',
      status: 'applied',
    },
  },
];

const statusFilters = [
  { value: '', label: 'All Applications' },
  { value: 'preparing', label: 'Preparing' },
  { value: 'ready', label: 'Ready' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
];

export default function Applications({ userId }: ApplicationsProps) {
  const [applications, setApplications] = useState<Application[]>(mockApplications);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');

  const filteredApplications = statusFilter
    ? applications.filter((app) => app.status === statusFilter)
    : applications;

  const handleUpdateStatus = async (appId: string, status: string, note?: string) => {
    // TODO: Call API
    setApplications((prev) =>
      prev.map((app) =>
        app.app_id === appId
          ? {
              ...app,
              status: status as Application['status'],
              timeline: [
                ...app.timeline,
                {
                  status,
                  date: new Date().toISOString(),
                  note: note || `Status changed to ${status}`,
                },
              ],
            }
          : app
      )
    );
  };

  const handleAddNote = async (appId: string, note: string) => {
    // TODO: Call API
    setApplications((prev) =>
      prev.map((app) =>
        app.app_id === appId
          ? {
              ...app,
              timeline: [
                ...app.timeline,
                {
                  status: app.status,
                  date: new Date().toISOString(),
                  note,
                },
              ],
            }
          : app
      )
    );
  };

  // Group by status for summary
  const statusCounts = applications.reduce((acc, app) => {
    acc[app.status] = (acc[app.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="text-gray-500 mt-1">
            Track and manage your job applications
          </p>
        </div>
        <button className="btn btn-secondary">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statusFilters.slice(1).map((filter) => (
          <button
            key={filter.value}
            onClick={() =>
              setStatusFilter(statusFilter === filter.value ? '' : filter.value)
            }
            className={`p-4 rounded-lg text-center transition-all ${
              statusFilter === filter.value
                ? 'bg-primary-100 border-2 border-primary-500'
                : 'bg-white border border-gray-200 hover:border-primary-300'
            }`}
          >
            <div className="text-2xl font-bold text-gray-900">
              {statusCounts[filter.value] || 0}
            </div>
            <div className="text-sm text-gray-500">{filter.label}</div>
          </button>
        ))}
      </div>

      {/* Filter Bar */}
      <div className="card flex items-center gap-4">
        <Filter className="w-5 h-5 text-gray-400" />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-auto"
        >
          {statusFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.label}
            </option>
          ))}
        </select>
        <span className="text-sm text-gray-500">
          Showing {filteredApplications.length} of {applications.length} applications
        </span>
      </div>

      {/* Applications List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        </div>
      ) : filteredApplications.length > 0 ? (
        <div className="space-y-4">
          {filteredApplications.map((app) => (
            <ApplicationCard
              key={app.app_id}
              application={app}
              onUpdateStatus={handleUpdateStatus}
              onAddNote={handleAddNote}
            />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No applications found.</p>
          <a href="/jobs" className="btn btn-primary mt-4 inline-flex">
            Browse Jobs
          </a>
        </div>
      )}
    </div>
  );
}
