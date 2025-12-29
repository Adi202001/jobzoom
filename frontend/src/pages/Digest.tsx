import { useState, useEffect } from 'react';
import {
  Calendar,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface DigestProps {
  userId: string;
}

interface DigestData {
  date: string;
  stats: {
    total_applications: number;
    submitted_today: number;
    interviews_scheduled: number;
    follow_ups_needed: number;
    response_rate: number;
  };
  action_items: {
    type: 'follow_up' | 'interview' | 'new_match';
    title: string;
    company: string;
    note: string;
    days?: number;
  }[];
  weekly_summary: {
    applications_submitted: number;
    interviews_scheduled: number;
    offers_received: number;
    rejections: number;
  };
}

const mockDigest: DigestData = {
  date: new Date().toISOString(),
  stats: {
    total_applications: 24,
    submitted_today: 2,
    interviews_scheduled: 4,
    follow_ups_needed: 3,
    response_rate: 29.2,
  },
  action_items: [
    {
      type: 'interview',
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc',
      note: 'Interview tomorrow at 2:00 PM PST',
    },
    {
      type: 'follow_up',
      title: 'Full Stack Developer',
      company: 'StartupXYZ',
      note: 'No response after 8 days',
      days: 8,
    },
    {
      type: 'follow_up',
      title: 'Backend Engineer',
      company: 'DataFlow',
      note: 'No response after 10 days',
      days: 10,
    },
    {
      type: 'new_match',
      title: 'Platform Engineer',
      company: 'CloudScale',
      note: '94% match - highly recommended',
    },
  ],
  weekly_summary: {
    applications_submitted: 8,
    interviews_scheduled: 2,
    offers_received: 1,
    rejections: 1,
  },
};

export default function Digest({ userId }: DigestProps) {
  const [digest, setDigest] = useState<DigestData>(mockDigest);
  const [loading, setLoading] = useState(false);
  const [showWeekly, setShowWeekly] = useState(true);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      // TODO: Fetch from API
      await new Promise((resolve) => setTimeout(resolve, 1000));
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'interview':
        return <Calendar className="w-5 h-5 text-green-600" />;
      case 'follow_up':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'new_match':
        return <TrendingUp className="w-5 h-5 text-blue-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getActionColor = (type: string) => {
    switch (type) {
      case 'interview':
        return 'border-l-green-500 bg-green-50';
      case 'follow_up':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'new_match':
        return 'border-l-blue-500 bg-blue-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Daily Digest</h1>
          <p className="text-gray-500 mt-1">
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="btn btn-secondary"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card text-center">
          <div className="text-3xl font-bold text-gray-900">
            {digest.stats.total_applications}
          </div>
          <div className="text-sm text-gray-500">Total Apps</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-green-600">
            {digest.stats.submitted_today}
          </div>
          <div className="text-sm text-gray-500">Sent Today</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-600">
            {digest.stats.interviews_scheduled}
          </div>
          <div className="text-sm text-gray-500">Interviews</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-yellow-600">
            {digest.stats.follow_ups_needed}
          </div>
          <div className="text-sm text-gray-500">Need Follow-up</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-purple-600">
            {digest.stats.response_rate}%
          </div>
          <div className="text-sm text-gray-500">Response Rate</div>
        </div>
      </div>

      {/* Action Items */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-primary-600" />
          Action Items
        </h2>
        <div className="space-y-3">
          {digest.action_items.map((item, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border-l-4 ${getActionColor(item.type)}`}
            >
              <div className="flex items-start gap-3">
                {getActionIcon(item.type)}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{item.title}</div>
                  <div className="text-sm text-gray-600">{item.company}</div>
                  <div className="text-sm text-gray-500 mt-1">{item.note}</div>
                </div>
                {item.type === 'follow_up' && (
                  <button className="btn btn-primary text-sm">
                    Send Follow-up
                  </button>
                )}
                {item.type === 'new_match' && (
                  <button className="btn btn-primary text-sm">
                    View & Apply
                  </button>
                )}
                {item.type === 'interview' && (
                  <button className="btn btn-secondary text-sm">
                    Prepare
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weekly Summary */}
      <div className="card">
        <button
          onClick={() => setShowWeekly(!showWeekly)}
          className="w-full flex items-center justify-between text-lg font-semibold text-gray-900"
        >
          <span className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            Weekly Summary
          </span>
          {showWeekly ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </button>

        {showWeekly && (
          <div className="mt-4 pt-4 border-t">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {digest.weekly_summary.applications_submitted}
                </div>
                <div className="text-sm text-blue-700">Apps Submitted</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {digest.weekly_summary.interviews_scheduled}
                </div>
                <div className="text-sm text-green-700">Interviews</div>
              </div>
              <div className="text-center p-4 bg-emerald-50 rounded-lg">
                <div className="text-2xl font-bold text-emerald-600">
                  {digest.weekly_summary.offers_received}
                </div>
                <div className="text-sm text-emerald-700">Offers</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {digest.weekly_summary.rejections}
                </div>
                <div className="text-sm text-red-700">Rejections</div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">This Week's Highlights</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Submitted {digest.weekly_summary.applications_submitted} new applications
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Response rate of {digest.stats.response_rate}% (above average!)
                </li>
                {digest.weekly_summary.offers_received > 0 && (
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Received {digest.weekly_summary.offers_received} offer(s) - congratulations!
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
        <h2 className="text-lg font-semibold text-primary-900 mb-3">
          💡 Tips for Today
        </h2>
        <ul className="space-y-2 text-primary-800">
          <li>• Follow up on applications that are 7+ days old</li>
          <li>• Prepare talking points for your upcoming interview</li>
          <li>• Review new job matches and apply to top recommendations</li>
        </ul>
      </div>
    </div>
  );
}
