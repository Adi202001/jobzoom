import { useState } from 'react';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Linkedin,
  Briefcase,
  DollarSign,
  Target,
  XCircle,
  CheckCircle,
  Plus,
  X,
} from 'lucide-react';
import ResumeUpload from '../components/ResumeUpload';

interface ProfileProps {
  userId: string | null;
  onProfileCreated: (userId: string) => void;
}

export default function Profile({ userId, onProfileCreated }: ProfileProps) {
  const [step, setStep] = useState(userId ? 3 : 1); // Start at resume if profile exists
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    target_titles: [] as string[],
    locations: [] as string[],
    remote_preference: 'any' as 'remote_only' | 'hybrid_ok' | 'onsite_ok' | 'any',
    salary_min: '',
    salary_max: '',
    blacklisted_companies: [] as string[],
    required_keywords: [] as string[],
  });

  const [newTitle, setNewTitle] = useState('');
  const [newLocation, setNewLocation] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const addToList = (field: keyof typeof formData, value: string, setValue: (s: string) => void) => {
    if (value.trim()) {
      setFormData((prev) => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()],
      }));
      setValue('');
    }
  };

  const removeFromList = (field: keyof typeof formData, index: number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: (prev[field] as string[]).filter((_, i) => i !== index),
    }));
  };

  const handleSubmitProfile = async () => {
    setIsLoading(true);
    try {
      // TODO: Call API to create profile
      // const result = await profileApi.create(formData);
      // onProfileCreated(result.user_id);

      // Mock response
      const mockUserId = `user_${Date.now()}`;
      onProfileCreated(mockUserId);
      setStep(3); // Move to resume upload
    } catch (error) {
      console.error('Failed to create profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResumeUpload = async (file: File) => {
    setIsLoading(true);
    try {
      // TODO: Upload resume to API
      // await resumeApi.upload(userId, file);

      // Mock success
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setUploadedFile(file.name);
    } catch (error) {
      console.error('Failed to upload resume:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextPaste = async (text: string) => {
    setIsLoading(true);
    try {
      // TODO: Parse resume text
      // await resumeApi.parse(userId, text);

      await new Promise((resolve) => setTimeout(resolve, 1500));
      setUploadedFile('Resume text parsed');
    } catch (error) {
      console.error('Failed to parse resume:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {userId ? 'Your Profile' : 'Create Your Profile'}
        </h1>
        <p className="text-gray-500 mt-1">
          {userId
            ? 'Manage your profile and preferences'
            : 'Set up your profile to start finding jobs'}
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-4 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                step >= s
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {step > s ? <CheckCircle className="w-5 h-5" /> : s}
            </div>
            <span
              className={`text-sm ${
                step >= s ? 'text-gray-900' : 'text-gray-400'
              }`}
            >
              {s === 1 ? 'Basic Info' : s === 2 ? 'Preferences' : 'Resume'}
            </span>
            {s < 3 && <div className="w-12 h-0.5 bg-gray-200" />}
          </div>
        ))}
      </div>

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <div className="card space-y-6">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="input pl-10"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input pl-10"
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="input pl-10"
                  placeholder="+1 (555) 000-0000"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="input pl-10"
                  placeholder="San Francisco, CA"
                />
              </div>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                LinkedIn
              </label>
              <div className="relative">
                <Linkedin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="url"
                  name="linkedin"
                  value={formData.linkedin}
                  onChange={handleInputChange}
                  className="input pl-10"
                  placeholder="https://linkedin.com/in/johndoe"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              disabled={!formData.name || !formData.email}
              className="btn btn-primary"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Preferences */}
      {step === 2 && (
        <div className="card space-y-6">
          <h2 className="text-lg font-semibold">Job Preferences</h2>

          {/* Target Titles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Briefcase className="inline w-4 h-4 mr-1" />
              Target Job Titles
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="input flex-1"
                placeholder="e.g., Software Engineer"
                onKeyDown={(e) =>
                  e.key === 'Enter' && addToList('target_titles', newTitle, setNewTitle)
                }
              />
              <button
                onClick={() => addToList('target_titles', newTitle, setNewTitle)}
                className="btn btn-secondary"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.target_titles.map((title, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                >
                  {title}
                  <button onClick={() => removeFromList('target_titles', idx)}>
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Preferred Locations */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <MapPin className="inline w-4 h-4 mr-1" />
              Preferred Locations
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                className="input flex-1"
                placeholder="e.g., San Francisco, Remote"
                onKeyDown={(e) =>
                  e.key === 'Enter' && addToList('locations', newLocation, setNewLocation)
                }
              />
              <button
                onClick={() => addToList('locations', newLocation, setNewLocation)}
                className="btn btn-secondary"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.locations.map((loc, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  {loc}
                  <button onClick={() => removeFromList('locations', idx)}>
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Remote Preference */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Remote Preference
            </label>
            <select
              name="remote_preference"
              value={formData.remote_preference}
              onChange={handleInputChange}
              className="input"
            >
              <option value="any">Any (Remote, Hybrid, or On-site)</option>
              <option value="remote_only">Remote Only</option>
              <option value="hybrid_ok">Remote or Hybrid</option>
              <option value="onsite_ok">Any including On-site</option>
            </select>
          </div>

          {/* Salary Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <DollarSign className="inline w-4 h-4 mr-1" />
              Salary Range (USD)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <input
                type="number"
                name="salary_min"
                value={formData.salary_min}
                onChange={handleInputChange}
                className="input"
                placeholder="Min (e.g., 100000)"
              />
              <input
                type="number"
                name="salary_max"
                value={formData.salary_max}
                onChange={handleInputChange}
                className="input"
                placeholder="Max (e.g., 150000)"
              />
            </div>
          </div>

          {/* Blacklisted Companies */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <XCircle className="inline w-4 h-4 mr-1" />
              Companies to Avoid
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newCompany}
                onChange={(e) => setNewCompany(e.target.value)}
                className="input flex-1"
                placeholder="Company name"
                onKeyDown={(e) =>
                  e.key === 'Enter' &&
                  addToList('blacklisted_companies', newCompany, setNewCompany)
                }
              />
              <button
                onClick={() =>
                  addToList('blacklisted_companies', newCompany, setNewCompany)
                }
                className="btn btn-secondary"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.blacklisted_companies.map((company, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                >
                  {company}
                  <button onClick={() => removeFromList('blacklisted_companies', idx)}>
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Required Keywords */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Target className="inline w-4 h-4 mr-1" />
              Must-Have Keywords
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                className="input flex-1"
                placeholder="e.g., React, Python"
                onKeyDown={(e) =>
                  e.key === 'Enter' &&
                  addToList('required_keywords', newKeyword, setNewKeyword)
                }
              />
              <button
                onClick={() =>
                  addToList('required_keywords', newKeyword, setNewKeyword)
                }
                className="btn btn-secondary"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.required_keywords.map((keyword, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                >
                  {keyword}
                  <button onClick={() => removeFromList('required_keywords', idx)}>
                    <X className="w-4 h-4" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <button onClick={() => setStep(1)} className="btn btn-secondary">
              Back
            </button>
            <button
              onClick={handleSubmitProfile}
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Creating...' : 'Continue'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Resume Upload */}
      {step === 3 && (
        <div className="card space-y-6">
          <h2 className="text-lg font-semibold">Upload Your Resume</h2>
          <p className="text-gray-500">
            Upload your resume so we can match you with the best jobs and
            auto-fill applications.
          </p>

          <ResumeUpload
            onUpload={handleResumeUpload}
            onTextPaste={handleTextPaste}
            isLoading={isLoading}
            uploadedFile={uploadedFile}
          />

          {uploadedFile && (
            <div className="flex justify-end">
              <a href="/" className="btn btn-primary">
                Go to Dashboard
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
