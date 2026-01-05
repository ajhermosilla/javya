import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { CalendarSetlist } from '../types/scheduling';
import './ScheduleCalendar.css';

interface ScheduleCalendarProps {
  year: number;
  month: number;
  setlists: CalendarSetlist[];
  onDateClick: (date: string) => void;
  onSetlistClick: (setlistId: string) => void;
}

interface CalendarDay {
  date: string;
  dayOfMonth: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  setlists: CalendarSetlist[];
}

export function ScheduleCalendar({
  year,
  month,
  setlists,
  onDateClick,
  onSetlistClick,
}: ScheduleCalendarProps) {
  const { t } = useTranslation();

  const days = useMemo(() => {
    const result: CalendarDay[] = [];
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Get the day of week for the first day (0 = Sunday, but we want 0 = Monday)
    let startDayOfWeek = firstDay.getDay() - 1;
    if (startDayOfWeek < 0) startDayOfWeek = 6;

    // Create setlists map for quick lookup by date
    const setlistMap = new Map<string, CalendarSetlist[]>();
    setlists.forEach((setlist) => {
      if (setlist.service_date) {
        const date = setlist.service_date;
        if (!setlistMap.has(date)) {
          setlistMap.set(date, []);
        }
        setlistMap.get(date)!.push(setlist);
      }
    });

    // Add days from previous month
    const prevMonth = new Date(year, month, 0);
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonth.getDate() - i;
      const date = new Date(year, month - 1, day);
      const dateStr = date.toISOString().split('T')[0];
      result.push({
        date: dateStr,
        dayOfMonth: day,
        isCurrentMonth: false,
        isToday: false,
        setlists: setlistMap.get(dateStr) || [],
      });
    }

    // Add days of current month
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split('T')[0];
      result.push({
        date: dateStr,
        dayOfMonth: day,
        isCurrentMonth: true,
        isToday: date.getTime() === today.getTime(),
        setlists: setlistMap.get(dateStr) || [],
      });
    }

    // Add days from next month to complete the grid
    const remainingDays = 42 - result.length;
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i);
      const dateStr = date.toISOString().split('T')[0];
      result.push({
        date: dateStr,
        dayOfMonth: i,
        isCurrentMonth: false,
        isToday: false,
        setlists: setlistMap.get(dateStr) || [],
      });
    }

    return result;
  }, [year, month, setlists]);

  const weekDays = [
    t('availability.weekdays.mon'),
    t('availability.weekdays.tue'),
    t('availability.weekdays.wed'),
    t('availability.weekdays.thu'),
    t('availability.weekdays.fri'),
    t('availability.weekdays.sat'),
    t('availability.weekdays.sun'),
  ];

  return (
    <div className="schedule-calendar">
      <div className="calendar-header">
        {weekDays.map((day) => (
          <div key={day} className="weekday">
            {day}
          </div>
        ))}
      </div>
      <div className="calendar-grid">
        {days.map((day) => (
          <div
            key={day.date}
            className={`calendar-day ${day.isCurrentMonth ? '' : 'other-month'} ${
              day.isToday ? 'today' : ''
            } ${day.setlists.length > 0 ? 'has-events' : ''}`}
            onClick={() => onDateClick(day.date)}
          >
            <span className="day-number">{day.dayOfMonth}</span>
            <div className="events">
              {day.setlists.slice(0, 3).map((setlist) => (
                <button
                  key={setlist.id}
                  className={`event-chip event-${setlist.event_type?.toLowerCase() || 'other'}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSetlistClick(setlist.id);
                  }}
                  title={setlist.name}
                >
                  <span className="event-name">{setlist.name}</span>
                  {setlist.assignments.length > 0 && (
                    <span className="team-count">
                      {setlist.assignments.length}
                    </span>
                  )}
                </button>
              ))}
              {day.setlists.length > 3 && (
                <span className="more-events">
                  +{day.setlists.length - 3} {t('scheduling.more')}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
