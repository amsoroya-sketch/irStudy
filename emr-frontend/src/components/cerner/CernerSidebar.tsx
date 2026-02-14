// src/components/cerner/CernerSidebar.tsx

import React, { useState, useEffect } from 'react';
import {
  Home,
  FileText,
  Pill,
  FlaskConical,
  ClipboardCheck,
  UserCircle,
  Clock,
  Settings
} from 'lucide-react';

interface CernerSidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  sessionId: string | null;
}

const navItems = [
  {
    id: 'dashboard',
    path: '/cerner',
    icon: Home,
    label: 'Dashboard',
    color: 'text-blue-600'
  },
  {
    id: 'soap-notes',
    path: '/cerner/soap-notes',
    icon: FileText,
    label: 'SOAP Notes',
    color: 'text-green-600'
  },
  {
    id: 'prescriptions',
    path: '/cerner/prescriptions',
    icon: Pill,
    label: 'Prescriptions',
    color: 'text-purple-600'
  },
  {
    id: 'pathology',
    path: '/cerner/pathology',
    icon: FlaskConical,
    label: 'Pathology',
    color: 'text-orange-600'
  },
  {
    id: 'orders',
    path: '/cerner/orders',
    icon: ClipboardCheck,
    label: 'Orders',
    color: 'text-red-600'
  },
  {
    id: 'patient',
    path: '/cerner/patient',
    icon: UserCircle,
    label: 'Patient Info',
    color: 'text-cyan-600'
  }
];

export const CernerSidebar: React.FC<CernerSidebarProps> = ({
  currentPath,
  onNavigate,
  sessionId
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (!sessionId) return;

    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [sessionId]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="cerner-sidebar">
      {/* Logo Section */}
      <div className="cerner-logo-section">
        <h1 className="text-xl font-bold text-white">Cerner</h1>
        <p className="text-xs text-gray-400 mt-1">PowerChart</p>
      </div>

      {/* Navigation Items */}
      <nav className="cerner-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.path;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.path)}
              className={`cerner-nav-item ${isActive ? 'active' : ''}`}>
              <Icon className={`w-5 h-5 ${isActive ? item.color : 'text-gray-400'}`} />
              <span className={isActive ? 'text-white font-medium' : 'text-gray-300'}>
                {item.label}
              </span>
              {isActive && <div className="cerner-active-indicator" />}
            </button>
          );
        })}
      </nav>

      {/* Session Timer */}
      {sessionId && (
        <div className="cerner-session-timer">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300">Time: {formatTime(elapsedTime)}</span>
        </div>
      )}

      {/* Settings */}
      <div className="cerner-settings">
        <button
          onClick={() => onNavigate('/cerner/settings')}
          className="cerner-settings-button"
        >
          <Settings className="w-5 h-5 text-gray-400" />
          <span className="text-gray-300">Settings</span>
        </button>
      </div>
    </div>
  );
};
