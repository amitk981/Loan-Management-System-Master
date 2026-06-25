import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface AppShellProps {
  activePage: string;
  onNavigate: (page: string) => void;
  onLogout?: () => void;
  children: React.ReactNode;
}

const AppShell: React.FC<AppShellProps> = ({ activePage, onNavigate, onLogout, children }) => {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header activePage={activePage} onLogout={onLogout} />
        <main className="flex-1 overflow-y-auto bg-slate-50">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
