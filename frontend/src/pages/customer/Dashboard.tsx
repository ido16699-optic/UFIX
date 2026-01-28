import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { jobService, orderService } from '../../services';
import { ClipboardList, Package, Clock, CheckCircle } from 'lucide-react';

export default function CustomerDashboard() {
  const { data: jobs } = useQuery({
    queryKey: ['myJobs'],
    queryFn: () => jobService.getMyJobRequests(1, 5),
  });

  const { data: orders } = useQuery({
    queryKey: ['myOrders'],
    queryFn: () => orderService.getMyOrders(1, 5),
  });

  const stats = [
    { label: 'Active Jobs', value: jobs?.items?.filter(j => j.status === 'open').length || 0, icon: ClipboardList },
    { label: 'Pending Orders', value: orders?.items?.filter(o => o.status === 'pending_payment').length || 0, icon: Clock },
    { label: 'In Progress', value: orders?.items?.filter(o => o.status === 'in_progress').length || 0, icon: Package },
    { label: 'Completed', value: orders?.items?.filter(o => o.status === 'completed').length || 0, icon: CheckCircle },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <Link to="/customer/new-job" className="btn-primary">
          + New Job Request
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <stat.icon className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Jobs */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Job Requests</h2>
        {jobs?.items?.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No job requests yet.{' '}
            <Link to="/customer/new-job" className="text-primary-600 hover:underline">
              Create your first request
            </Link>
          </p>
        ) : (
          <div className="space-y-3">
            {jobs?.items?.slice(0, 5).map((job) => (
              <Link
                key={job.id}
                to={`/customer/jobs/${job.id}`}
                className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{job.title}</h3>
                    <p className="text-sm text-gray-500 capitalize">{job.category.replace('_', ' ')}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    job.status === 'open' ? 'bg-green-100 text-green-700' :
                    job.status === 'matched' ? 'bg-blue-100 text-blue-700' :
                    job.status === 'completed' ? 'bg-gray-100 text-gray-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {job.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
