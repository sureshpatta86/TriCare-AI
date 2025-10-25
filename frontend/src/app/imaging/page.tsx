'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDropzone } from 'react-dropzone';
import { Image as ImageIcon, Upload, Loader2, AlertCircle, Activity } from 'lucide-react';
import { imagingFileSchema, type ImagingFileData } from '@/lib/validations/schemas';
import { prescreenImage } from '@/lib/api-client';
import ProgressIndicator from '@/components/shared/ProgressIndicator';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8011';

interface PrescreenResult {
  prediction: string;
  confidence: number;
  explanation?: string;
  heatmap_base64?: string;
  model_used: string;
}

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

export default function ImagingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PrescreenResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageType, setImageType] = useState<string>('x-ray');
  const [correlationId, setCorrelationId] = useState<string | null>(null);
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([
    { id: '1', label: 'Uploading image', status: 'pending' },
    { id: '2', label: 'Validating file', status: 'pending' },
    { id: '3', label: 'Analyzing with AI', status: 'pending' },
    { id: '4', label: 'Generating results', status: 'pending' },
  ]);

  const {
    setValue,
    handleSubmit,
    formState: { errors },
    clearErrors
  } = useForm<ImagingFileData>({
    resolver: zodResolver(imagingFileSchema)
  });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.dcm']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const selectedFile = acceptedFiles[0];
        setFile(selectedFile);
        setValue('file', selectedFile);
        clearErrors('file');
        setError(null);
        setResult(null);

        // Create preview
        const reader = new FileReader();
        reader.onload = () => {
          setPreview(reader.result as string);
        };
        reader.readAsDataURL(selectedFile);
      }
    }
  });

  const onSubmit = async (data: ImagingFileData) => {
    if (!data.file) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setCorrelationId(null);

    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('image_type', imageType);

    try {
      // Step 1: Uploading
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 300)); // Brief delay for UX
      
      // Step 2: Validating
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 0 ? { ...step, status: 'completed' } : 
        idx === 1 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Step 3: Analyzing
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 1 ? { ...step, status: 'completed' } : 
        idx === 2 ? { ...step, status: 'active' } : step
      ));

      const response = await prescreenImage(
        data.file,
        imageType
      );
      
      // Step 4: Generating results
      setProgressSteps(prev => prev.map((step, idx) => 
        idx === 2 ? { ...step, status: 'completed' } : 
        idx === 3 ? { ...step, status: 'active' } : step
      ));
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Complete
      setProgressSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));
      setResult(response);
      
    } catch (err: unknown) {
      const axiosError = err as { 
        response?: { 
          data?: { detail?: string; correlation_id?: string }; 
          headers?: Record<string, string>;
          status?: number;
        } 
      };
      
      // Extract correlation ID from error response
      const corrId = axiosError.response?.headers?.['x-correlation-id'] || 
                     axiosError.response?.data?.correlation_id;
      if (corrId) {
        setCorrelationId(corrId);
      }
      
      // Mark current step as error
      setProgressSteps(prev => prev.map(step => 
        step.status === 'active' ? { ...step, status: 'error' } : step
      ));
      
      // Enhanced error messages based on status code
      if (axiosError.response?.status === 413) {
        setError('File is too large. Maximum size is 10MB.');
      } else if (axiosError.response?.status === 415) {
        setError('Unsupported file type. Please upload JPEG, PNG, or DICOM images.');
      } else if (axiosError.response?.status === 429) {
        setError('Too many requests. Please wait a moment and try again.');
      } else {
        setError(axiosError.response?.data?.detail || 'Failed to analyze image. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full mb-4">
              <ImageIcon className="w-8 h-8 text-purple-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Medical Imaging Pre-Screen
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Upload a medical image for AI-powered preliminary analysis
            </p>
          </div>

          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <form onSubmit={handleSubmit(onSubmit)}>
              {/* Image Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Imaging Type
                </label>
                <select
                  value={imageType}
                  onChange={(e) => setImageType(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="x-ray">X-ray</option>
                  <option value="ct">CT Scan</option>
                  <option value="mri">MRI</option>
                </select>
                <div className="mt-2 flex items-start gap-2 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-amber-800 dark:text-amber-200">
                    <strong>Important:</strong> Please ensure you select the correct imaging type that matches your uploaded image. 
                    The AI analysis is optimized based on the type you select. Mismatched types may result in inaccurate analysis.
                  </p>
                </div>
              </div>

              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? 'border-purple-500 bg-purple-50'
                    : errors.file
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-300 dark:border-gray-600 hover:border-purple-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                {preview ? (
                  <div className="space-y-4">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={preview}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg shadow-md"
                    />
                    <p className="text-lg font-medium text-gray-900 dark:text-white">
                      {file?.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {file && (file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2">
                      Drop your medical image here, or click to browse
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Supports PNG, JPG, JPEG, DICOM (Max 10MB)
                    </p>
                  </div>
                )}
              </div>
              {errors.file && (
                <p className="mt-2 text-sm text-red-600">{errors.file.message as string}</p>
              )}

              {file && (
                <>
                  <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-1">
                          Verify Image Type Before Analysis
                        </h4>
                        <p className="text-sm text-blue-800 dark:text-blue-300 mb-2">
                          You selected: <strong className="uppercase">{imageType}</strong>
                        </p>
                        <p className="text-xs text-blue-700 dark:text-blue-400">
                          Please confirm that "{file.name}" is indeed a <strong>{imageType.toUpperCase()}</strong> image. 
                          If not, please change the imaging type above before analyzing.
                        </p>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-6 bg-purple-600 hover:bg-purple-700 dark:bg-purple-500 dark:hover:bg-purple-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white font-semibold py-4 px-6 rounded-xl transition-colors flex items-center justify-center"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Activity className="w-5 h-5 mr-2" />
                        Analyze Image
                      </>
                    )}
                  </button>
                </>
              )}
            </form>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-8">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-red-900 dark:text-red-200 mb-1">Error</h3>
                  <p className="text-red-700 dark:text-red-300 mb-2">{error}</p>
                  {correlationId && (
                    <div className="mt-3 pt-3 border-t border-red-200 dark:border-red-800">
                      <p className="text-xs text-red-600 dark:text-red-400 font-mono">
                        Request ID: {correlationId}
                      </p>
                      <p className="text-xs text-red-500 dark:text-red-500 mt-1">
                        Please save this ID if you need support assistance
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Loading Progress */}
          {loading && (
            <div className="mb-8">
              <ProgressIndicator steps={progressSteps} correlationId={correlationId || undefined} />
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Analysis Results
              </h2>

              <div className="grid md:grid-cols-2 gap-8">
                {/* Left: Images */}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                      Original X-ray
                    </h3>
                    {preview && (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={preview}
                        alt="Original"
                        className="w-full rounded-lg shadow-md border border-gray-200 dark:border-gray-700"
                      />
                    )}
                  </div>

                  {result.heatmap_base64 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                        Attention Heatmap
                      </h3>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={`data:image/png;base64,${result.heatmap_base64}`}
                        alt="Heatmap"
                        className="w-full rounded-lg shadow-md border border-gray-200 dark:border-gray-700"
                      />
                      <p className="text-xs text-gray-500 mt-2 italic">
                        Red areas indicate regions the AI model focused on
                      </p>
                    </div>
                  )}
                </div>

                {/* Right: Prediction */}
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
                      Prediction
                    </h3>
                    <div className="mb-4">
                      <p className="text-2xl font-bold text-purple-700 mb-2">
                        {result.prediction}
                      </p>
                      <div className="flex items-center">
                        <div className="flex-grow bg-gray-200 rounded-full h-3 mr-3">
                          <div
                            className="bg-purple-600 h-3 rounded-full transition-all"
                            style={{ width: `${result.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-gray-700">
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Model: {result.model_used}
                    </p>
                  </div>

                  {result.explanation && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
                        AI Explanation
                      </h3>
                      <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                        <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                          {result.explanation}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="font-semibold text-yellow-900 mb-2 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      Important Notice
                    </h4>
                    <p className="text-sm text-yellow-800">
                      This is a preliminary AI screening tool only. It is NOT a medical diagnosis. 
                      Always consult with a qualified radiologist or healthcare provider for accurate 
                      interpretation and treatment decisions.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
