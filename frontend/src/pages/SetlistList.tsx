import { useTranslation } from 'react-i18next';
import './SetlistList.css';

export function SetlistList() {
  const { t } = useTranslation();

  return (
    <div className="setlist-list-page">
      <header className="page-header">
        <h1>{t('setlists.title')}</h1>
        <button className="add-button">
          {t('setlists.addSetlist')}
        </button>
      </header>

      <div className="coming-soon">
        {t('setlists.comingSoon')}
      </div>
    </div>
  );
}
