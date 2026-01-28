import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { jobService } from '../../services';
import { CreateJobRequest, ServiceCategory, RequestType } from '../../types';
import { Loader2, MapPin } from 'lucide-react';

const categories = [
  { value: ServiceCategory.PLUMBING, label: 'Plumbing', emoji: '🔧' },
  { value: ServiceCategory.ELECTRICAL, label: 'Electrical', emoji: '⚡' },
  { value: ServiceCategory.PAINTING, label: 'Painting', emoji: '🎨' },
  { value: ServiceCategory.FURNITURE_ASSEMBLY, label: 'Furniture Assembly', emoji: '🪑' },
  { value: ServiceCategory.GENERAL_HANDYMAN, label: 'General Handyman', emoji: '🛠️' },
];

export default function CreateJobRequest() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CreateJobRequest>({
    defaultValues: {
      request_type: RequestType.ASAP,
      latitude: 0,
      longitude: 0,
    },
  });

  const selectedCategory = watch('category');
  const requestType = watch('request_type');

  const createMutation = useMutation({
    mutationFn: jobService.createJobRequest,
    onSuccess: () => {
      toast.success('Job request created successfully!');
      navigate('/customer/jobs');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create job request');
    },
  });

  const onSubmit = (data: CreateJobRequest) => {
    // For MVP, set dummy coordinates if not provided
    if (!data.latitude || !data.longitude) {
      data.latitude = 40.7128; // Default NYC
      data.longitude = -74.006;
    }
    createMutation.mutate(data);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setValue('latitude', position.coords.latitude);
          setValue('longitude', position.coords.longitude);
          toast.success('Location detected!');
        },
        () => {
          toast.error('Could not get your location');
        }
      );
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Create Job Request</h1>

      {/* Progress indicator */}
      <div className="flex items-center mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                s <= step ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}
            >
              {s}
            </div>
            {s < 3 && (
              <div className={`w-16 h-1 ${s < step ? 'bg-primary-600' : 'bg-gray-200'}`} />
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
        {/* Step 1: Category */}
        {step === 1 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">What do you need help with?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {categories.map((cat) => (
                <label
                  key={cat.value}
                  className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                    selectedCategory === cat.value
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    value={cat.value}
                    {...register('category', { required: 'Please select a category' })}
                    className="sr-only"
                  />
                  <span className="text-2xl mr-3">{cat.emoji}</span>
                  <span className="font-medium">{cat.label}</span>
                </label>
              ))}
            </div>
            {errors.category && (
              <p className="mt-2 text-sm text-red-600">{errors.category.message}</p>
            )}
            <button
              type="button"
              onClick={() => selectedCategory && setStep(2)}
              className="mt-6 w-full btn-primary py-3"
              disabled={!selectedCategory}
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 2: Details */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">Tell us more about the job</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                {...register('title', {
                  required: 'Title is required',
                  minLength: { value: 5, message: 'Title must be at least 5 characters' },
                })}
                className="input-field"
                placeholder="e.g., Fix leaking kitchen faucet"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                {...register('description', {
                  required: 'Description is required',
                  minLength: { value: 10, message: 'Please provide more details' },
                })}
                rows={4}
                className="input-field"
                placeholder="Describe the issue in detail..."
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                When do you need this done?
              </label>
              <div className="grid grid-cols-2 gap-3">
                <label
                  className={`flex items-center justify-center p-3 border-2 rounded-lg cursor-pointer ${
                    requestType === RequestType.ASAP
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200'
                  }`}
                >
                  <input
                    type="radio"
                    value={RequestType.ASAP}
                    {...register('request_type')}
                    className="sr-only"
                  />
                  <span className="font-medium">ASAP</span>
                </label>
                <label
                  className={`flex items-center justify-center p-3 border-2 rounded-lg cursor-pointer ${
                    requestType === RequestType.SCHEDULED
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200'
                  }`}
                >
                  <input
                    type="radio"
                    value={RequestType.SCHEDULED}
                    {...register('request_type')}
                    className="sr-only"
                  />
                  <span className="font-medium">Schedule</span>
                </label>
              </div>
            </div>

            {requestType === RequestType.SCHEDULED && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Date & Time
                </label>
                <input
                  type="datetime-local"
                  {...register('scheduled_date')}
                  className="input-field"
                />
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 btn-secondary py-3"
              >
                Back
              </button>
              <button
                type="button"
                onClick={() => setStep(3)}
                className="flex-1 btn-primary py-3"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Location */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">Where is the job location?</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <input
                type="text"
                {...register('address', { required: 'Address is required' })}
                className="input-field"
                placeholder="Enter your address"
              />
              {errors.address && (
                <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
              )}
            </div>

            <button
              type="button"
              onClick={getCurrentLocation}
              className="flex items-center gap-2 text-primary-600 hover:text-primary-700"
            >
              <MapPin size={18} />
              Use my current location
            </button>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex-1 btn-secondary py-3"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="flex-1 btn-primary py-3 flex items-center justify-center gap-2"
              >
                {createMutation.isPending && <Loader2 className="animate-spin" size={20} />}
                {createMutation.isPending ? 'Creating...' : 'Create Request'}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
