import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { UserRole } from './types';

// Layouts
import MainLayout from './components/layouts/MainLayout';
import AuthLayout from './components/layouts/AuthLayout';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Customer Pages
import CustomerDashboard from './pages/customer/Dashboard';
import CreateJobRequest from './pages/customer/CreateJobRequest';
import MyJobRequests from './pages/customer/MyJobRequests';
import JobDetails from './pages/customer/JobDetails';

// Handyman Pages
import HandymanDashboard from './pages/handyman/Dashboard';
import AvailableJobs from './pages/handyman/AvailableJobs';
import MyOffers from './pages/handyman/MyOffers';

// Shared Pages
import OrdersPage from './pages/shared/OrdersPage';
import OrderDetails from './pages/shared/OrderDetails';
import ChatPage from './pages/shared/ChatPage';
import ProfilePage from './pages/shared/ProfilePage';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import VerificationReview from './pages/admin/VerificationReview';

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    // Redirect to appropriate dashboard based on role
    if (user.role === UserRole.CUSTOMER) {
      return <Navigate to="/customer" replace />;
    } else if (user.role === UserRole.HANDYMAN) {
      return <Navigate to="/handyman" replace />;
    } else if (user.role === UserRole.ADMIN) {
      return <Navigate to="/admin" replace />;
    }
  }

  return <>{children}</>;
}

function App() {
  const { isAuthenticated, user } = useAuthStore();

  // Redirect authenticated users to their dashboard
  const getDefaultRedirect = () => {
    if (!user) return '/login';
    switch (user.role) {
      case UserRole.CUSTOMER:
        return '/customer';
      case UserRole.HANDYMAN:
        return '/handyman';
      case UserRole.ADMIN:
        return '/admin';
      default:
        return '/login';
    }
  };

  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to={getDefaultRedirect()} replace /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to={getDefaultRedirect()} replace /> : <RegisterPage />}
        />
      </Route>

      {/* Customer Routes */}
      <Route
        element={
          <ProtectedRoute allowedRoles={[UserRole.CUSTOMER]}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/customer" element={<CustomerDashboard />} />
        <Route path="/customer/new-job" element={<CreateJobRequest />} />
        <Route path="/customer/jobs" element={<MyJobRequests />} />
        <Route path="/customer/jobs/:id" element={<JobDetails />} />
        <Route path="/customer/orders" element={<OrdersPage />} />
        <Route path="/customer/orders/:id" element={<OrderDetails />} />
        <Route path="/customer/chat" element={<ChatPage />} />
        <Route path="/customer/profile" element={<ProfilePage />} />
      </Route>

      {/* Handyman Routes */}
      <Route
        element={
          <ProtectedRoute allowedRoles={[UserRole.HANDYMAN]}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/handyman" element={<HandymanDashboard />} />
        <Route path="/handyman/jobs" element={<AvailableJobs />} />
        <Route path="/handyman/offers" element={<MyOffers />} />
        <Route path="/handyman/orders" element={<OrdersPage />} />
        <Route path="/handyman/orders/:id" element={<OrderDetails />} />
        <Route path="/handyman/chat" element={<ChatPage />} />
        <Route path="/handyman/profile" element={<ProfilePage />} />
      </Route>

      {/* Admin Routes */}
      <Route
        element={
          <ProtectedRoute allowedRoles={[UserRole.ADMIN]}>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/verifications" element={<VerificationReview />} />
      </Route>

      {/* Default redirect */}
      <Route path="/" element={<Navigate to={isAuthenticated ? getDefaultRedirect() : '/login'} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
