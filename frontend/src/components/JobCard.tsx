import {
  MapPin,
  Building2,
  Clock,
  DollarSign,
  ExternalLink,
  Briefcase,
  Wifi,
} from 'lucide-react';
import type { Job, JobMatch } from '../types';

interface JobCardProps {
  job: Job | JobMatch;
  onApply?: (jobId: string) => void;
  showMatchScore?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 85) return 'score-excellent';
  if (score >= 70) return 'score-good';
  if (score >= 50) return 'score-fair';
  return 'score-low';
}

function getRemoteIcon(status: string) {
  switch (status) {
    case 'remote':
      return <Wifi className="w-4 h-4" />;
    case 'hybrid':
      return <Building2 className="w-4 h-4" />;
    default:
      return <MapPin className="w-4 h-4" />;
  }
}

function formatSalary(range: { min: number | null; max: number | null }): string {
  if (!range.min && !range.max) return 'Not specified';
  if (range.min && range.max) {
    return `$${(range.min / 1000).toFixed(0)}k - $${(range.max / 1000).toFixed(0)}k`;
  }
  if (range.min) return `$${(range.min / 1000).toFixed(0)}k+`;
  return `Up to $${(range.max! / 1000).toFixed(0)}k`;
}

export default function JobCard({ job, onApply, showMatchScore = true }: JobCardProps) {
  const matchScore = 'match_score' in job ? (job as JobMatch).match_score : null;
  const highlights = 'highlights' in job ? (job as JobMatch).highlights : [];

  return (
    <div className="card card-hover">
      <div className="flex items-start justify-between gap-4">
        {/* Job info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-lg text-gray-900 truncate">
              {job.title}
            </h3>
            {matchScore !== null && showMatchScore && (
              <span
                className={`badge ${getScoreColor(matchScore)} font-bold`}
              >
                {matchScore}% match
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 text-gray-600 mb-3">
            <Building2 className="w-4 h-4" />
            <span className="font-medium">{job.company}</span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded-md text-sm text-gray-600">
              {getRemoteIcon(job.remote_status)}
              {job.remote_status.charAt(0).toUpperCase() + job.remote_status.slice(1)}
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded-md text-sm text-gray-600">
              <MapPin className="w-4 h-4" />
              {job.location || 'Location not specified'}
            </span>
            {job.salary_range && (job.salary_range.min || job.salary_range.max) && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 rounded-md text-sm text-green-700">
                <DollarSign className="w-4 h-4" />
                {formatSalary(job.salary_range)}
              </span>
            )}
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded-md text-sm text-gray-600">
              <Briefcase className="w-4 h-4" />
              {job.job_type}
            </span>
          </div>

          {/* Description preview */}
          <p className="text-gray-600 text-sm line-clamp-2 mb-3">
            {job.description || 'No description available'}
          </p>

          {/* Highlights */}
          {highlights.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {highlights.map((highlight, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded"
                >
                  {highlight}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          {onApply && (
            <button
              onClick={() => onApply(job.job_id)}
              className="btn btn-primary"
            >
              Apply
            </button>
          )}
          {job.application_url && (
            <a
              href={job.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
            >
              <ExternalLink className="w-4 h-4" />
              View
            </a>
          )}
        </div>
      </div>

      {/* Posted date */}
      {job.posted_date && (
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center gap-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          Posted {new Date(job.posted_date).toLocaleDateString()}
        </div>
      )}
    </div>
  );
}
