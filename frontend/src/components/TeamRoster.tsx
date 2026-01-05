import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { ServiceRole } from '../types/scheduling';
import './TeamRoster.css';

interface TeamMember {
  id: string;
  user_id: string;
  user_name: string;
  service_role: ServiceRole;
  confirmed: boolean;
}

interface TeamRosterProps {
  assignments: TeamMember[];
  compact?: boolean;
  onMemberClick?: (assignmentId: string) => void;
}

const ROLE_ORDER: ServiceRole[] = [
  'worship_leader',
  'vocalist',
  'guitarist',
  'bassist',
  'drummer',
  'keys',
  'sound',
  'projection',
  'other',
];

export function TeamRoster({
  assignments,
  compact = false,
  onMemberClick,
}: TeamRosterProps) {
  const { t } = useTranslation();

  const groupedByRole = useMemo(() => {
    const groups = new Map<ServiceRole, TeamMember[]>();

    // Initialize groups in order
    ROLE_ORDER.forEach((role) => groups.set(role, []));

    // Group assignments
    assignments.forEach((assignment) => {
      const role = assignment.service_role;
      const group = groups.get(role);
      if (group) {
        group.push(assignment);
      }
    });

    // Filter out empty groups
    return Array.from(groups.entries()).filter(([, members]) => members.length > 0);
  }, [assignments]);

  if (assignments.length === 0) {
    return (
      <div className={`team-roster ${compact ? 'compact' : ''}`}>
        <p className="empty-roster">{t('scheduling.noAssignments')}</p>
      </div>
    );
  }

  return (
    <div className={`team-roster ${compact ? 'compact' : ''}`}>
      {groupedByRole.map(([role, members]) => (
        <div key={role} className="role-group">
          <span className="role-label">{t(`serviceRoles.${role}`)}</span>
          <div className="members">
            {members.map((member) => (
              <button
                key={member.id}
                className={`member-chip ${member.confirmed ? 'confirmed' : 'pending'}`}
                onClick={() => onMemberClick?.(member.id)}
                disabled={!onMemberClick}
              >
                <span className="member-name">{member.user_name}</span>
                {!compact && (
                  <span className={`status-badge ${member.confirmed ? 'confirmed' : 'pending'}`}>
                    {member.confirmed ? t('scheduling.confirmed') : t('scheduling.pending')}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
