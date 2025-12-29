import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  User,
  Briefcase,
  FileText,
  Mail,
  LogOut,
  Rocket,
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  userId: string | null;
  onLogout: () => void;
}

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/profile', icon: User, label: 'Profile' },
  { path: '/jobs', icon: Briefcase, label: 'Jobs' },
  { path: '/applications', icon: FileText, label: 'Applications' },
  { path: '/digest', icon: Mail, label: 'Digest' },
];

export default function Layout({ children, userId, onLogout }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
              <Rocket className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg">JobCopilot</h1>
              <p className="text-xs text-gray-400">AI Job Assistant</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User section */}
        {userId && (
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center justify-between">
              <div className="text-sm">
                <p className="text-gray-400">Logged in as</p>
                <p className="text-white font-medium truncate w-32">
                  {userId.slice(0, 12)}...
                </p>
              </div>
              <button
                onClick={onLogout}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
