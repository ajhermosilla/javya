import { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useAvailability } from '../hooks/useAvailability';
import { AvailabilityCalendar } from '../components/AvailabilityCalendar';
import { PatternEditor } from '../components/PatternEditor';
import type { AvailabilityStatus } from '../types/availability';
import './AvailabilityPage.css';

function getMonthRange(year: number, month: number) {
  const startDate = new Date(year, month, 1);
  const endDate = new Date(year, month + 1, 0);
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
}

export function AvailabilityPage() {
  const { t } = useTranslation();
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [showPatterns, setShowPatterns] = useState(false);

  const { startDate, endDate } = useMemo(
    () => getMonthRange(currentYear, currentMonth),
    [currentYear, currentMonth]
  );

  const {
    availability,
    patterns,
    loading,
    error,
    setDateAvailability,
    deleteAvailability,
    createPattern,
    updatePattern,
    deletePattern,
  } = useAvailability({ startDate, endDate });

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

  const handleDateClick = async (date: string, currentStatus: AvailabilityStatus | null) => {
    // Cycle through statuses: null -> available -> unavailable -> maybe -> null
    const statusCycle: (AvailabilityStatus | null)[] = [
      null,
      'available',
      'unavailable',
      'maybe',
    ];
    const currentIndex = statusCycle.indexOf(currentStatus);
    const nextStatus = statusCycle[(currentIndex + 1) % statusCycle.length];

    if (nextStatus === null) {
      // Find and delete the availability entry
      const entry = availability.find((a) => a.date === date);
      if (entry) {
        await deleteAvailability(entry.id);
      }
    } else {
      await setDateAvailability({ date, status: nextStatus });
    }
  };

  const monthName = new Date(currentYear, currentMonth).toLocaleDateString(
    undefined,
    { month: 'long', year: 'numeric' }
  );

  if (loading) {
    return (
      <div className="availability-page">
        <div className="loading">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="availability-page">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="availability-page">
      <header className="page-header">
        <h1>{t('availability.title')}</h1>
        <button
          className="btn-secondary"
          onClick={() => setShowPatterns(!showPatterns)}
        >
          {showPatterns
            ? t('availability.hidePatterns')
            : t('availability.showPatterns')}
        </button>
      </header>

      <div className="calendar-nav">
        <button onClick={handlePrevMonth} className="nav-button">
          ←
        </button>
        <span className="month-name">{monthName}</span>
        <button onClick={handleNextMonth} className="nav-button">
          →
        </button>
      </div>

      <div className="legend">
        <div className="legend-item">
          <span className="legend-color available"></span>
          {t('availability.status.available')}
        </div>
        <div className="legend-item">
          <span className="legend-color unavailable"></span>
          {t('availability.status.unavailable')}
        </div>
        <div className="legend-item">
          <span className="legend-color maybe"></span>
          {t('availability.status.maybe')}
        </div>
      </div>

      <p className="help-text">{t('availability.clickToChange')}</p>

      <AvailabilityCalendar
        year={currentYear}
        month={currentMonth}
        availability={availability}
        onDateClick={handleDateClick}
      />

      {showPatterns && (
        <PatternEditor
          patterns={patterns}
          onCreate={createPattern}
          onUpdate={updatePattern}
          onDelete={deletePattern}
        />
      )}
    </div>
  );
}
