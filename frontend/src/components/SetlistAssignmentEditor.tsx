import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSetlistAssignments, useTeamAvailability } from '../hooks/useScheduling';
import { SERVICE_ROLES, type ServiceRole, type SetlistAssignmentCreate } from '../types/scheduling';
import './SetlistAssignmentEditor.css';

interface User {
  id: string;
  name: string;
  email: string;
}

interface SetlistAssignmentEditorProps {
  setlistId: string;
  setlistName: string;
  serviceDate: string | null;
  users: User[];
  onClose: () => void;
}

export function SetlistAssignmentEditor({
  setlistId,
  setlistName,
  serviceDate,
  users,
  onClose,
}: SetlistAssignmentEditorProps) {
  const { t } = useTranslation();
  const [selectedRole, setSelectedRole] = useState<ServiceRole>('vocalist');
  const [selectedUserId, setSelectedUserId] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);

  const {
    assignments,
    loading,
    createAssignment,
    deleteAssignment,
    confirmAssignment,
  } = useSetlistAssignments(setlistId);

  const { teamAvailability } = useTeamAvailability(serviceDate);

  // Create a map of user availability for quick lookup
  const availabilityMap = new Map(
    teamAvailability.map((ta) => [ta.user_id, ta.availability_status])
  );

  const handleAddAssignment = async () => {
    if (!selectedUserId) {
      setError(t('scheduling.selectUser'));
      return;
    }

    try {
      setError(null);
      const data: SetlistAssignmentCreate = {
        user_id: selectedUserId,
        service_role: selectedRole,
        notes: notes || undefined,
      };
      await createAssignment(data);
      setSelectedUserId('');
      setNotes('');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('scheduling.addFailed'));
    }
  };

  const handleDeleteAssignment = async (assignmentId: string) => {
    try {
      await deleteAssignment(assignmentId);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('scheduling.deleteFailed'));
    }
  };

  const handleToggleConfirm = async (assignmentId: string, currentConfirmed: boolean) => {
    try {
      await confirmAssignment(assignmentId, !currentConfirmed);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('scheduling.confirmFailed'));
    }
  };

  const getAvailabilityClass = (userId: string) => {
    const status = availabilityMap.get(userId);
    if (!status) return '';
    return `avail-${status}`;
  };

  const getAvailabilityLabel = (userId: string) => {
    const status = availabilityMap.get(userId);
    if (!status) return '';
    return t(`availability.status.${status}`);
  };

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="assignment-editor-overlay" onClick={onClose}>
      <div className="assignment-editor" onClick={(e) => e.stopPropagation()}>
        <header className="editor-header">
          <h2>{t('scheduling.editAssignments')}</h2>
          <p className="setlist-info">{setlistName}</p>
          <button className="close-btn" onClick={onClose}>
            &times;
          </button>
        </header>

        {error && <div className="error-message">{error}</div>}

        <div className="editor-body">
          <section className="add-section">
            <h3>{t('scheduling.addAssignment')}</h3>
            <div className="add-form">
              <div className="form-row">
                <label htmlFor="role-select">{t('scheduling.role')}</label>
                <select
                  id="role-select"
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value as ServiceRole)}
                >
                  {SERVICE_ROLES.map((role) => (
                    <option key={role} value={role}>
                      {t(`serviceRoles.${role}`)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <label htmlFor="user-select">{t('scheduling.teamMember')}</label>
                <select
                  id="user-select"
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                >
                  <option value="">{t('scheduling.selectUser')}</option>
                  {users.map((user) => (
                    <option
                      key={user.id}
                      value={user.id}
                      className={getAvailabilityClass(user.id)}
                    >
                      {user.name} {getAvailabilityLabel(user.id) && `(${getAvailabilityLabel(user.id)})`}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <label htmlFor="notes-input">{t('scheduling.notes')}</label>
                <input
                  id="notes-input"
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={t('scheduling.notesPlaceholder')}
                />
              </div>

              <button
                className="add-btn"
                onClick={handleAddAssignment}
                disabled={!selectedUserId}
              >
                {t('scheduling.addMember')}
              </button>
            </div>
          </section>

          <section className="current-section">
            <h3>{t('scheduling.currentAssignments')}</h3>
            {loading ? (
              <p className="loading">{t('common.loading')}</p>
            ) : assignments.length === 0 ? (
              <p className="empty">{t('scheduling.noAssignments')}</p>
            ) : (
              <ul className="assignment-list">
                {assignments.map((assignment) => (
                  <li key={assignment.id} className="assignment-item">
                    <div className="assignment-info">
                      <span className="role-name">
                        {t(`serviceRoles.${assignment.service_role}`)}
                      </span>
                      <span className="user-name">{assignment.user_name}</span>
                      {assignment.notes && (
                        <span className="assignment-notes">{assignment.notes}</span>
                      )}
                    </div>
                    <div className="assignment-actions">
                      <button
                        className={`confirm-btn ${assignment.confirmed ? 'confirmed' : ''}`}
                        onClick={() =>
                          handleToggleConfirm(assignment.id, assignment.confirmed)
                        }
                        title={
                          assignment.confirmed
                            ? t('scheduling.markPending')
                            : t('scheduling.markConfirmed')
                        }
                      >
                        {assignment.confirmed ? t('scheduling.confirmed') : t('scheduling.pending')}
                      </button>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteAssignment(assignment.id)}
                        title={t('common.delete')}
                      >
                        &times;
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
