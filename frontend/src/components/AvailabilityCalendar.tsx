import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { Availability, AvailabilityStatus } from '../types/availability';
import './AvailabilityCalendar.css';

interface AvailabilityCalendarProps {
  year: number;
  month: number;
  availability: Availability[];
  onDateClick: (date: string, currentStatus: AvailabilityStatus | null) => void;
}

interface CalendarDay {
  date: string;
  dayOfMonth: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  status: AvailabilityStatus | null;
  note: string | null;
}

export function AvailabilityCalendar({
  year,
  month,
  availability,
  onDateClick,
}: AvailabilityCalendarProps) {
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

    // Create availability map for quick lookup
    const availMap = new Map(
      availability.map((a) => [a.date, { status: a.status, note: a.note }])
    );

    // Add days from previous month
    const prevMonth = new Date(year, month, 0);
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonth.getDate() - i;
      const date = new Date(year, month - 1, day);
      const dateStr = date.toISOString().split('T')[0];
      const avail = availMap.get(dateStr);
      result.push({
        date: dateStr,
        dayOfMonth: day,
        isCurrentMonth: false,
        isToday: false,
        status: avail?.status ?? null,
        note: avail?.note ?? null,
      });
    }

    // Add days of current month
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      const dateStr = date.toISOString().split('T')[0];
      const avail = availMap.get(dateStr);
      result.push({
        date: dateStr,
        dayOfMonth: day,
        isCurrentMonth: true,
        isToday: date.getTime() === today.getTime(),
        status: avail?.status ?? null,
        note: avail?.note ?? null,
      });
    }

    // Add days from next month to complete the grid
    const remainingDays = 42 - result.length; // 6 rows * 7 days
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i);
      const dateStr = date.toISOString().split('T')[0];
      const avail = availMap.get(dateStr);
      result.push({
        date: dateStr,
        dayOfMonth: i,
        isCurrentMonth: false,
        isToday: false,
        status: avail?.status ?? null,
        note: avail?.note ?? null,
      });
    }

    return result;
  }, [year, month, availability]);

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
    <div className="availability-calendar">
      <div className="calendar-header">
        {weekDays.map((day) => (
          <div key={day} className="weekday">
            {day}
          </div>
        ))}
      </div>
      <div className="calendar-grid">
        {days.map((day) => (
          <button
            key={day.date}
            className={`calendar-day ${day.isCurrentMonth ? '' : 'other-month'} ${
              day.isToday ? 'today' : ''
            } ${day.status ? `status-${day.status}` : ''}`}
            onClick={() => onDateClick(day.date, day.status)}
            title={day.note || undefined}
          >
            <span className="day-number">{day.dayOfMonth}</span>
            {day.status && (
              <span className={`status-indicator ${day.status}`}></span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
