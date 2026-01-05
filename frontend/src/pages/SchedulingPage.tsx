import { useState, useMemo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useCalendar } from '../hooks/useScheduling';
import { ScheduleCalendar } from '../components/ScheduleCalendar';
import { ScheduleList } from '../components/ScheduleList';
import { SetlistAssignmentEditor } from '../components/SetlistAssignmentEditor';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api/client';
import type { CalendarSetlist } from '../types/scheduling';
import './SchedulingPage.css';

type ViewMode = 'calendar' | 'list';

function getMonthRange(year: number, month: number) {
  const startDate = new Date(year, month, 1);
  const endDate = new Date(year, month + 1, 0);
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
}

interface User {
  id: string;
  name: string;
  email: string;
}

export function SchedulingPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [viewMode, setViewMode] = useState<ViewMode>('calendar');
  const [editingSetlist, setEditingSetlist] = useState<CalendarSetlist | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [usersError, setUsersError] = useState<string | null>(null);

  const { startDate, endDate } = useMemo(
    () => getMonthRange(currentYear, currentMonth),
    [currentYear, currentMonth]
  );

  const { setlists, loading, error, refetch } = useCalendar({ startDate, endDate });

  const isAdminOrLeader = user?.role === 'admin' || user?.role === 'leader';

  // Fetch users for assignment editor
  useEffect(() => {
    if (isAdminOrLeader) {
      setUsersError(null);
      api.get<User[]>('/api/v1/users/')
        .then(setUsers)
        .catch((err) => {
          console.error(err);
          setUsersError(t('scheduling.usersLoadError'));
        });
    }
  }, [isAdminOrLeader, t]);

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const handleDateClick = (date: string) => {
    // Future: could open a day detail view
    console.log('Date clicked:', date);
  };

  const handleSetlistClick = (setlistId: string) => {
    const setlist = setlists.find((s) => s.id === setlistId);
    if (setlist && isAdminOrLeader) {
      setEditingSetlist(setlist);
    } else {
      // Navigate to setlist detail
      navigate(`/setlists/${setlistId}`);
    }
  };

  const handleCloseEditor = () => {
    setEditingSetlist(null);
    refetch();
  };

  const monthName = new Date(currentYear, currentMonth).toLocaleDateString(
    undefined,
    { month: 'long', year: 'numeric' }
  );

  if (loading) {
    return (
      <div className="scheduling-page">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="scheduling-page">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="scheduling-page">
      <header className="page-header">
        <h1>{t('scheduling.title')}</h1>
        <div className="view-toggle">
          <button
            className={`toggle-btn ${viewMode === 'calendar' ? 'active' : ''}`}
            onClick={() => setViewMode('calendar')}
          >
            {t('scheduling.calendarView')}
          </button>
          <button
            className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            {t('scheduling.listView')}
          </button>
        </div>
      </header>

      <div className="calendar-nav">
        <button onClick={handlePrevMonth} className="nav-button">
          &larr;
        </button>
        <span className="month-name">{monthName}</span>
        <button onClick={handleNextMonth} className="nav-button">
          &rarr;
        </button>
      </div>

      {usersError && (
        <div className="warning-banner">{usersError}</div>
      )}

      {viewMode === 'calendar' ? (
        <ScheduleCalendar
          year={currentYear}
          month={currentMonth}
          setlists={setlists}
          onDateClick={handleDateClick}
          onSetlistClick={handleSetlistClick}
        />
      ) : (
        <ScheduleList
          setlists={setlists}
          onSetlistClick={handleSetlistClick}
        />
      )}

      {editingSetlist && isAdminOrLeader && user && (
        <SetlistAssignmentEditor
          setlistId={editingSetlist.id}
          setlistName={editingSetlist.name}
          serviceDate={editingSetlist.service_date}
          users={users}
          currentUserId={user.id}
          onClose={handleCloseEditor}
        />
      )}
    </div>
  );
}
