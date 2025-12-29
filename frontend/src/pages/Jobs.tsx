import { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  RefreshCw,
  Plus,
  ExternalLink,
  Loader2,
} from 'lucide-react';
import JobCard from '../components/JobCard';
import type { JobMatch } from '../types';

interface JobsProps {
  userId: string;
}

// Mock data
const mockJobs: JobMatch[] = [
  {
    job_id: '1',
    title: 'Senior Software Engineer',
    company: 'TechCorp Inc',
    location: 'San Francisco, CA',
    remote_status: 'hybrid',
    salary_range: { min: 150000, max: 200000 },
    job_type: 'full-time',
    posted_date: '2024-01-15',
    description: 'We are looking for a senior software engineer to join our team and help build the next generation of our platform. You will work with a talented team of engineers on challenging problems at scale.',
    requirements: ['Python', 'React', '5+ years experience', 'System Design'],
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
    description: 'Join our fast-growing startup as a full stack developer. You\'ll have the opportunity to work on a variety of projects and make a real impact.',
    requirements: ['JavaScript', 'Node.js', 'PostgreSQL', 'AWS'],
    responsibilities: [],
    application_url: 'https://example.com/apply',
    source_url: 'https://example.com',
    scraped_at: '2024-01-14T10:00:00Z',
    status: 'matched',
    match_score: 87,
    highlights: ['Full remote', 'Startup culture'],
  },
  {
    job_id: '3',
    title: 'Backend Engineer',
    company: 'BigTech Corp',
    location: 'New York, NY',
    remote_status: 'onsite',
    salary_range: { min: 140000, max: 180000 },
    job_type: 'full-time',
    posted_date: '2024-01-13',
    description: 'We\'re looking for a backend engineer to help us scale our infrastructure and build new services.',
    requirements: ['Go', 'Kubernetes', 'Microservices'],
    responsibilities: [],
    application_url: 'https://example.com/apply',
    source_url: 'https://example.com',
    scraped_at: '2024-01-13T10:00:00Z',
    status: 'matched',
    match_score: 78,
    highlights: ['Great benefits', 'Career growth'],
  },
  {
    job_id: '4',
    title: 'DevOps Engineer',
    company: 'CloudNine',
    location: 'Austin, TX',
    remote_status: 'hybrid',
    salary_range: { min: 130000, max: 170000 },
    job_type: 'full-time',
    posted_date: '2024-01-12',
    description: 'Looking for a DevOps engineer to help us improve our CI/CD pipelines and infrastructure.',
    requirements: ['Docker', 'Terraform', 'AWS', 'CI/CD'],
    responsibilities: [],
    application_url: 'https://example.com/apply',
    source_url: 'https://example.com',
    scraped_at: '2024-01-12T10:00:00Z',
    status: 'matched',
    match_score: 72,
    highlights: ['Modern stack'],
  },
];

export default function Jobs({ userId }: JobsProps) {
  const [jobs, setJobs] = useState<JobMatch[]>(mockJobs);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showScrapeModal, setShowScrapeModal] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [scraping, setScraping] = useState(false);
  const [filter, setFilter] = useState<'all' | 'remote' | 'hybrid' | 'onsite'>('all');
  const [minScore, setMinScore] = useState(0);

  const filteredJobs = jobs.filter((job) => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      if (
        !job.title.toLowerCase().includes(query) &&
        !job.company.toLowerCase().includes(query)
      ) {
        return false;
      }
    }

    // Remote filter
    if (filter !== 'all' && job.remote_status !== filter) {
      return false;
    }

    // Score filter
    if (job.match_score < minScore) {
      return false;
    }

    return true;
  });

  const handleScrape = async () => {
    if (!scrapeUrl) return;

    setScraping(true);
    try {
      // TODO: Call API
      // await jobApi.scrape(scrapeUrl, userId);

      await new Promise((resolve) => setTimeout(resolve, 2000));
      setShowScrapeModal(false);
      setScrapeUrl('');
      // TODO: Refresh jobs list
    } catch (error) {
      console.error('Failed to scrape:', error);
    } finally {
      setScraping(false);
    }
  };

  const handleApply = async (jobId: string) => {
    // TODO: Implement application flow
    console.log('Applying to job:', jobId);
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      // TODO: Call API to refresh recommendations
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
          <p className="text-gray-500 mt-1">
            {filteredJobs.length} jobs matching your profile
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="btn btn-secondary"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => setShowScrapeModal(true)}
            className="btn btn-primary"
          >
            <Plus className="w-4 h-4" />
            Add Source
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10"
                placeholder="Search jobs..."
              />
            </div>
          </div>

          {/* Remote filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="input w-auto"
          >
            <option value="all">All Locations</option>
            <option value="remote">Remote Only</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">On-site</option>
          </select>

          {/* Score filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Min Score:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-24"
            />
            <span className="text-sm font-medium w-12">{minScore}%</span>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        </div>
      ) : filteredJobs.length > 0 ? (
        <div className="space-y-4">
          {filteredJobs.map((job) => (
            <JobCard key={job.job_id} job={job} onApply={handleApply} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No jobs found matching your criteria.</p>
          <button
            onClick={() => setShowScrapeModal(true)}
            className="btn btn-primary mt-4"
          >
            <Plus className="w-4 h-4" />
            Add Job Source
          </button>
        </div>
      )}

      {/* Scrape Modal */}
      {showScrapeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold mb-4">Add Job Source</h2>
            <p className="text-gray-500 text-sm mb-4">
              Enter a company careers page URL to scrape job listings.
            </p>

            <input
              type="url"
              value={scrapeUrl}
              onChange={(e) => setScrapeUrl(e.target.value)}
              className="input mb-4"
              placeholder="https://boards.greenhouse.io/company"
            />

            <div className="text-xs text-gray-400 mb-4">
              Supported: Greenhouse, Lever, Workday, Ashby
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowScrapeModal(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleScrape}
                disabled={!scrapeUrl || scraping}
                className="btn btn-primary"
              >
                {scraping ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Scraping...
                  </>
                ) : (
                  <>
                    <ExternalLink className="w-4 h-4" />
                    Scrape Jobs
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
