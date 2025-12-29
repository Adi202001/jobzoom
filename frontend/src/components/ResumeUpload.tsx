import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface ResumeUploadProps {
  onUpload: (file: File) => Promise<void>;
  onTextPaste?: (text: string) => void;
  isLoading?: boolean;
  uploadedFile?: string | null;
}

export default function ResumeUpload({
  onUpload,
  onTextPaste,
  isLoading = false,
  uploadedFile = null,
}: ResumeUploadProps) {
  const [error, setError] = useState<string | null>(null);
  const [showTextInput, setShowTextInput] = useState(false);
  const [resumeText, setResumeText] = useState('');

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setError(null);
      const file = acceptedFiles[0];

      if (!file) return;

      // Validate file type
      const validTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
      ];

      if (!validTypes.includes(file.type)) {
        setError('Please upload a PDF, Word document, or text file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      try {
        await onUpload(file);
      } catch (err) {
        setError('Failed to upload file. Please try again.');
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: isLoading,
  });

  const handleTextSubmit = () => {
    if (resumeText.trim() && onTextPaste) {
      onTextPaste(resumeText);
    }
  };

  if (uploadedFile) {
    return (
      <div className="border-2 border-green-200 bg-green-50 rounded-xl p-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-green-800">Resume uploaded successfully!</p>
            <p className="text-sm text-green-600">{uploadedFile}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-secondary text-sm"
          >
            Upload New
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />

        {isLoading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
            <p className="text-gray-600">Processing resume...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <div>
              <p className="font-medium text-gray-700">
                {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or click to browse (PDF, DOCX, TXT)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Text input toggle */}
      <div className="text-center">
        <button
          type="button"
          onClick={() => setShowTextInput(!showTextInput)}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          {showTextInput ? 'Hide text input' : 'Or paste resume text'}
        </button>
      </div>

      {/* Text input area */}
      {showTextInput && (
        <div className="space-y-3">
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume text here..."
            className="input min-h-[200px] resize-y"
          />
          <button
            type="button"
            onClick={handleTextSubmit}
            disabled={!resumeText.trim()}
            className="btn btn-primary w-full"
          >
            <FileText className="w-4 h-4" />
            Parse Resume Text
          </button>
        </div>
      )}
    </div>
  );
}
