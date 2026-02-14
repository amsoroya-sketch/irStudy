import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  FileText,
  Pill,
  Activity,
  FlaskConical,
  Clock,
  Settings,
  ChevronRight,
  User
} from 'lucide-react';
import { motion } from 'framer-motion';

interface EpicSidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  sessionId?: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
}

export const EpicSidebar: React.FC<EpicSidebarProps> = ({
  currentPath,
  onNavigate,
  sessionId
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['chart']));

  // Timer for session tracking
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

  const navigationItems: NavItem[] = [
    {
      id: 'notes',
      label: 'Notes',
      icon: <FileText size={20} />,
      path: '/epic/notes'
    },
    {
      id: 'orders',
      label: 'Orders',
      icon: <ClipboardList size={20} />,
      path: '/epic/orders',
      badge: 0
    },
    {
      id: 'medications',
      label: 'Medications',
      icon: <Pill size={20} />,
      path: '/epic/medications'
    },
    {
      id: 'results',
      label: 'Results',
      icon: <FlaskConical size={20} />,
      path: '/epic/results'
    },
    {
      id: 'flowsheet',
      label: 'Flowsheet',
      icon: <Activity size={20} />,
      path: '/epic/flowsheet'
    }
  ];

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  return (
    <div className="epic-sidebar">
      {/* Patient Context Bar */}
      <div className="epic-sidebar-patient">
        <div className="flex items-center gap-3">
          <div className="epic-patient-avatar">
            <User size={20} />
          </div>
          <div className="flex-1">
            <div className="epic-patient-name">Smith, John</div>
            <div className="epic-patient-mrn">MRN: 12345678</div>
          </div>
        </div>
      </div>

      {/* Session Timer */}
      {sessionId && (
        <div className="epic-timer">
          <Clock size={16} className="text-epic-primary" />
          <span className="epic-timer-text">{formatTime(elapsedTime)}</span>
        </div>
      )}

      {/* Navigation Sections */}
      <nav className="epic-nav">
        <div className="epic-nav-section">
          <button
            className="epic-nav-section-header"
            onClick={() => toggleSection('chart')}
          >
            <ChevronRight
              size={16}
              className={`epic-nav-chevron ${expandedSections.has('chart') ? 'expanded' : ''}`}
            />
            <span>Chart Review</span>
          </button>

          {expandedSections.has('chart') && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="epic-nav-items"
            >
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.path)}
                  className={`epic-nav-item ${
                    currentPath === item.path ? 'active' : ''
                  }`}
                >
                  <span className="epic-nav-icon">{item.icon}</span>
                  <span className="epic-nav-label">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="epic-nav-badge">{item.badge}</span>
                  )}
                </button>
              ))}
            </motion.div>
          )}
        </div>
      </nav>

      {/* Settings Button */}
      <div className="epic-sidebar-footer">
        <button className="epic-settings-btn">
          <Settings size={18} />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
};
