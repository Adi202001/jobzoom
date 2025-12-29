import { useState, useEffect } from 'react';
import {
  Briefcase,
  FileText,
  TrendingUp,
  Calendar,
  Target,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import StatsCard from '../components/StatsCard';
import JobCard from '../components/JobCard';
import type { JobMatch, DashboardStats } from '../types';

interface DashboardProps {
  userId: string;
}

// Mock data for demonstration
const mockStats: DashboardStats = {
  total_applications: 24,
  by_status: {
    preparing: 3,
    ready: 2,
    submitted: 12,
    interview: 4,
    offer: 1,
    rejected: 2,
  },
  response_rate: 29.2,
  interviews_scheduled: 4,
  new_matches: 8,
};

const mockRecommendations: JobMatch[] = [
  {
    job_id: '1',
    title: 'Senior Software Engineer',
    company: 'TechCorp Inc',
    location: 'San Francisco, CA',
    remote_status: 'hybrid',
    salary_range: { min: 150000, max: 200000 },
    job_type: 'full-time',
    posted_date: '2024-01-15',
    description: 'We are looking for a senior software engineer to join our team...',
    requirements: ['Python', 'React', '5+ years experience'],
    responsibilities: [],
    application_url: 'https://example.com/apply',
    source_url: 'https://example.com',
    scraped_at: '2024-01-15T10:00:00Z',
    status: 'matched',
    match_score: 92,
    highlights: ['Skills match', 'Remote friendly', 'Salary in range'],
  },
  {
    job_id: '2',
    title: 'Full Stack Developer',
    company: 'StartupXYZ',
    location: 'Remote',
    remote_status: 'remote',
    salary_range: { min: 120000, max: 160000 },
    job_type: 'full-time',
    posted_date: '2024-01-14',
    description: 'Join our fast-growing startup as a full stack developer...',
    requirements: ['JavaScript', 'Node.js', 'PostgreSQL'],
    responsibilities: [],
    application_url: 'https://example.com/apply',
    source_url: 'https://example.com',
    scraped_at: '2024-01-14T10:00:00Z',
    status: 'matched',
    match_score: 87,
    highlights: ['Full remote', 'Startup culture'],
  },
];

export default function Dashboard({ userId }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats>(mockStats);
  const [recommendations, setRecommendations] = useState<JobMatch[]>(mockRecommendations);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // TODO: Fetch real data from API
    // dashboardApi.getStats(userId).then(setStats);
    // jobApi.getRecommendations(userId).then(setRecommendations);
  }, [userId]);

  const handleApply = (jobId: string) => {
    // TODO: Implement apply flow
    console.log('Apply to job:', jobId);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">
          Welcome back! Here's your job search overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Applications"
          value={stats.total_applications}
          icon={FileText}
          color="blue"
          trend={{ value: 12, isPositive: true }}
        />
        <StatsCard
          title="Interviews"
          value={stats.interviews_scheduled}
          subtitle="Scheduled this week"
          icon={Calendar}
          color="green"
        />
        <StatsCard
          title="Response Rate"
          value={`${stats.response_rate}%`}
          icon={TrendingUp}
          color="purple"
        />
        <StatsCard
          title="New Matches"
          value={stats.new_matches}
          subtitle="Since yesterday"
          icon={Target}
          color="yellow"
        />
      </div>

      {/* Pipeline Overview */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Application Pipeline
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(stats.by_status).map(([status, count]) => {
            const icons: Record<string, typeof Clock> = {
              preparing: Clock,
              ready: CheckCircle,
              submitted: FileText,
              interview: Calendar,
              offer: Target,
              rejected: AlertCircle,
            };
            const colors: Record<string, string> = {
              preparing: 'text-gray-600 bg-gray-100',
              ready: 'text-blue-600 bg-blue-100',
              submitted: 'text-yellow-600 bg-yellow-100',
              interview: 'text-green-600 bg-green-100',
              offer: 'text-emerald-600 bg-emerald-100',
              rejected: 'text-red-600 bg-red-100',
            };
            const Icon = icons[status] || Clock;

            return (
              <div
                key={status}
                className="text-center p-4 rounded-lg bg-gray-50"
              >
                <div
                  className={`w-10 h-10 rounded-full ${colors[status]} flex items-center justify-center mx-auto mb-2`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-xs text-gray-500 capitalize">
                  {status.replace('_', ' ')}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Recommendations */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Top Recommendations
          </h2>
          <a
            href="/jobs"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            View all jobs →
          </a>
        </div>
        <div className="space-y-4">
          {recommendations.map((job) => (
            <JobCard key={job.job_id} job={job} onApply={handleApply} />
          ))}
        </div>
      </div>

      {/* Action Items */}
      <div className="card bg-primary-50 border-primary-200">
        <h2 className="text-lg font-semibold text-primary-900 mb-3">
          Action Items
        </h2>
        <ul className="space-y-2">
          <li className="flex items-center gap-2 text-primary-800">
            <AlertCircle className="w-4 h-4" />
            <span>3 applications need follow-up (7+ days since submission)</span>
          </li>
          <li className="flex items-center gap-2 text-primary-800">
            <Calendar className="w-4 h-4" />
            <span>Interview with TechCorp tomorrow at 2:00 PM</span>
          </li>
          <li className="flex items-center gap-2 text-primary-800">
            <Target className="w-4 h-4" />
            <span>8 new job matches found - review and apply</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
