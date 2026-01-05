import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import './Layout.css';

type Page = 'songs' | 'setlists' | 'availability';

interface LayoutProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  children: ReactNode;
}

export function Layout({ currentPage, onNavigate, children }: LayoutProps) {
  return (
    <div className="layout">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
