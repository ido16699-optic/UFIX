import { Outlet } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">UFIX</h1>
          <p className="text-primary-200">Find trusted handymen near you</p>
        </div>
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
