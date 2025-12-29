import { useState } from 'react';
import {
  Building2,
  Calendar,
  ChevronDown,
  ChevronUp,
  FileText,
  MessageSquare,
  Clock,
} from 'lucide-react';
import type { Application } from '../types';

interface ApplicationCardProps {
  application: Application;
  onUpdateStatus: (appId: string, status: string, note?: string) => void;
  onAddNote: (appId: string, note: string) => void;
}

const statusColors: Record<string, string> = {
  preparing: 'badge-gray',
  ready: 'badge-blue',
  submitted: 'badge-yellow',
  interview: 'badge-green',
  offer: 'bg-green-500 text-white',
  rejected: 'badge-red',
};

const statusLabels: Record<string, string> = {
  preparing: 'Preparing',
  ready: 'Ready to Apply',
  submitted: 'Submitted',
  interview: 'Interview',
  offer: 'Offer!',
  rejected: 'Rejected',
};

const statusOptions = [
  { value: 'preparing', label: 'Preparing' },
  { value: 'ready', label: 'Ready to Apply' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
];

export default function ApplicationCard({
  application,
  onUpdateStatus,
  onAddNote,
}: ApplicationCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [showNoteInput, setShowNoteInput] = useState(false);
  const [noteText, setNoteText] = useState('');
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);

  const handleStatusChange = (newStatus: string) => {
    onUpdateStatus(application.app_id, newStatus);
    setShowStatusDropdown(false);
  };

  const handleAddNote = () => {
    if (noteText.trim()) {
      onAddNote(application.app_id, noteText);
      setNoteText('');
      setShowNoteInput(false);
    }
  };

  const daysSinceSubmission = application.submitted_at
    ? Math.floor(
        (Date.now() - new Date(application.submitted_at).getTime()) /
          (1000 * 60 * 60 * 24)
      )
    : null;

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-lg text-gray-900">
              {application.job?.title || 'Unknown Position'}
            </h3>
            <div className="relative">
              <button
                onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                className={`badge ${statusColors[application.status]} cursor-pointer hover:opacity-80`}
              >
                {statusLabels[application.status]}
              </button>
              {showStatusDropdown && (
                <div className="absolute top-full left-0 mt-1 bg-white shadow-lg rounded-lg border py-1 z-10 min-w-[150px]">
                  {statusOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleStatusChange(option.value)}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${
                        option.value === application.status
                          ? 'bg-gray-50 font-medium'
                          : ''
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4 text-gray-600 text-sm">
            <span className="flex items-center gap-1">
              <Building2 className="w-4 h-4" />
              {application.job?.company || 'Unknown Company'}
            </span>
            {application.submitted_at && (
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                Submitted {new Date(application.submitted_at).toLocaleDateString()}
              </span>
            )}
            {daysSinceSubmission !== null && daysSinceSubmission > 0 && (
              <span className="flex items-center gap-1 text-yellow-600">
                <Clock className="w-4 h-4" />
                {daysSinceSubmission} days ago
              </span>
            )}
          </div>
        </div>

        {/* Match score */}
        <div className="text-right">
          <div className="text-2xl font-bold text-primary-600">
            {application.match_score}%
          </div>
          <div className="text-xs text-gray-500">match</div>
        </div>
      </div>

      {/* Expand toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-sm text-gray-500 mt-4 hover:text-gray-700"
      >
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        {expanded ? 'Hide details' : 'Show details'}
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="mt-4 pt-4 border-t space-y-4">
          {/* Timeline */}
          {application.timeline.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Timeline
              </h4>
              <div className="space-y-2 pl-6 border-l-2 border-gray-200">
                {application.timeline.map((entry, idx) => (
                  <div key={idx} className="relative">
                    <div className="absolute -left-[25px] w-3 h-3 bg-primary-500 rounded-full" />
                    <div className="text-sm">
                      <span className="font-medium">{statusLabels[entry.status] || entry.status}</span>
                      <span className="text-gray-500 ml-2">
                        {new Date(entry.date).toLocaleDateString()}
                      </span>
                      {entry.note && (
                        <p className="text-gray-600 mt-1">{entry.note}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          <div className="flex gap-4">
            {application.tailored_resume && (
              <button className="btn btn-secondary text-sm">
                <FileText className="w-4 h-4" />
                View Resume
              </button>
            )}
            {application.cover_letter && (
              <button className="btn btn-secondary text-sm">
                <FileText className="w-4 h-4" />
                View Cover Letter
              </button>
            )}
          </div>

          {/* Add note */}
          <div>
            {!showNoteInput ? (
              <button
                onClick={() => setShowNoteInput(true)}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <MessageSquare className="w-4 h-4" />
                Add a note
              </button>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Add a note..."
                  className="input flex-1"
                  onKeyDown={(e) => e.key === 'Enter' && handleAddNote()}
                />
                <button onClick={handleAddNote} className="btn btn-primary">
                  Add
                </button>
                <button
                  onClick={() => {
                    setShowNoteInput(false);
                    setNoteText('');
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
