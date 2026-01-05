import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { LanguageSwitcher } from './LanguageSwitcher';
import './Sidebar.css';

type Page = 'songs' | 'setlists' | 'availability';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!collapsed && <h1 className="sidebar-logo">Javya</h1>}
        <button
          className="collapse-button"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`nav-item ${currentPage === 'songs' ? 'active' : ''}`}
          onClick={() => onNavigate('songs')}
        >
          <span className="nav-icon">♪</span>
          {!collapsed && <span className="nav-label">{t('nav.songs')}</span>}
        </button>
        <button
          className={`nav-item ${currentPage === 'setlists' ? 'active' : ''}`}
          onClick={() => onNavigate('setlists')}
        >
          <span className="nav-icon">☰</span>
          {!collapsed && <span className="nav-label">{t('nav.setlists')}</span>}
        </button>
        <button
          className={`nav-item ${currentPage === 'availability' ? 'active' : ''}`}
          onClick={() => onNavigate('availability')}
        >
          <span className="nav-icon">📅</span>
          {!collapsed && <span className="nav-label">{t('nav.availability')}</span>}
        </button>
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <>
            <LanguageSwitcher />
            {user && (
              <div className="user-section">
                <div className="user-info">
                  <span className="user-name">{user.name}</span>
                  <span className="user-role">{t(`roles.${user.role}`)}</span>
                </div>
                <button className="logout-button" onClick={logout}>
                  {t('auth.logout')}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
