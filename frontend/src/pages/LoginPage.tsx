import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, register, isLoading } = useAuth();

  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (isRegistering) {
        await register({ email, password, name });
      } else {
        await login({ email, password });
      }
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('auth.error.generic'));
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1 className="app-name">Javya</h1>
          <p className="app-tagline">{t('auth.tagline')}</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>{isRegistering ? t('auth.register') : t('auth.login')}</h2>

          {error && <div className="error-message">{error}</div>}

          {isRegistering && (
            <div className="form-group">
              <label htmlFor="name">{t('auth.name')}</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={1}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">{t('auth.email')}</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('auth.password')}</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={submitting}
          >
            {submitting
              ? t('common.loading')
              : isRegistering
                ? t('auth.register')
                : t('auth.login')}
          </button>
        </form>

        <div className="toggle-mode">
          {isRegistering ? (
            <p>
              {t('auth.hasAccount')}{' '}
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(false);
                  setError('');
                }}
              >
                {t('auth.login')}
              </button>
            </p>
          ) : (
            <p>
              {t('auth.noAccount')}{' '}
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(true);
                  setError('');
                }}
              >
                {t('auth.register')}
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
