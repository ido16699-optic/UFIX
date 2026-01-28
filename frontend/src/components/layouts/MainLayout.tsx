import { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { UserRole } from '../../types';
import {
  Home,
  Briefcase,
  MessageSquare,
  User,
  Menu,
  X,
  LogOut,
  ClipboardList,
  DollarSign,
  Shield,
  FileCheck,
} from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

const customerNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/customer', icon: <Home size={20} /> },
  { label: 'New Request', path: '/customer/new-job', icon: <ClipboardList size={20} /> },
  { label: 'My Jobs', path: '/customer/jobs', icon: <Briefcase size={20} /> },
  { label: 'Orders', path: '/customer/orders', icon: <DollarSign size={20} /> },
  { label: 'Chat', path: '/customer/chat', icon: <MessageSquare size={20} /> },
  { label: 'Profile', path: '/customer/profile', icon: <User size={20} /> },
];

const handymanNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/handyman', icon: <Home size={20} /> },
  { label: 'Available Jobs', path: '/handyman/jobs', icon: <Briefcase size={20} /> },
  { label: 'My Offers', path: '/handyman/offers', icon: <ClipboardList size={20} /> },
  { label: 'Orders', path: '/handyman/orders', icon: <DollarSign size={20} /> },
  { label: 'Chat', path: '/handyman/chat', icon: <MessageSquare size={20} /> },
  { label: 'Profile', path: '/handyman/profile', icon: <User size={20} /> },
];

const adminNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/admin', icon: <Home size={20} /> },
  { label: 'Verifications', path: '/admin/verifications', icon: <FileCheck size={20} /> },
];

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();

  const getNavItems = (): NavItem[] => {
    switch (user?.role) {
      case UserRole.CUSTOMER:
        return customerNavItems;
      case UserRole.HANDYMAN:
        return handymanNavItems;
      case UserRole.ADMIN:
        return adminNavItems;
      default:
        return [];
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = getNavItems();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <Link to="/" className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">UFIX</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900 text-sm">{user?.name}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 w-full px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top bar */}
        <header className="bg-white shadow-sm sticky top-0 z-30">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <Menu size={24} />
            </button>
            <div className="flex-1 lg:hidden text-center">
              <span className="font-semibold text-gray-900">UFIX</span>
            </div>
            <div className="w-10 lg:hidden" /> {/* Spacer for centering */}
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
