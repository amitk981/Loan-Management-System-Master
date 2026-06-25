import React, { useState } from 'react';
import { Agentation } from 'agentation';
import { RoleProvider, useRole } from './contexts/RoleContext';
import { Role } from './types';
import AppShell from './components/layout/AppShell';
import LoginScreen from './pages/auth/LoginScreen';
import BorrowerPortal from './pages/borrower/BorrowerPortal';

import Dashboard from './pages/Dashboard';
import ApplicationList from './pages/applications/ApplicationList';
import ApplicationDetail from './pages/applications/ApplicationDetail';
import NewApplication from './pages/applications/NewApplication';
import MemberDirectory from './pages/members/MemberDirectory';
import MemberProfile from './pages/members/MemberProfile';
import Borrower360 from './pages/members/Borrower360';
import AppraisalWorkbench from './pages/appraisal/AppraisalWorkbench';
import SanctionWorkbench from './pages/sanction/SanctionWorkbench';
import DocumentationHub from './pages/documentation/DocumentationHub';
import DisbursementHub from './pages/disbursement/DisbursementHub';
import LoanAccount360 from './pages/loan-accounts/LoanAccount360';
import RepaymentsHub from './pages/repayments/RepaymentsHub';
import MonitoringDashboard from './pages/monitoring/MonitoringDashboard';
import ComplianceDashboard from './pages/compliance/ComplianceDashboard';
import RegistersHub from './pages/registers/RegistersHub';
import TaskInbox from './pages/tasks/TaskInbox';
import DefaultRecoveryHub from './pages/defaults/DefaultRecoveryHub';
import LoanClosureHub from './pages/closure/LoanClosureHub';
import InterestManagement from './pages/interest/InterestManagement';
import SettingsHub from './pages/settings/SettingsHub';
import ReportsMIS from './pages/reports/ReportsMIS';

export type Page =
  | 'dashboard' | 'tasks'
  | 'applications' | 'applications/new' | 'applications/detail'
  | 'members' | 'members/profile' | 'members/borrower360'
  | 'appraisal' | 'sanction'
  | 'documentation' | 'disbursement' | 'cfc'
  | 'interest'
  | 'loan-accounts' | 'loan-accounts/detail'
  | 'repayments' | 'monitoring'
  | 'defaults' | 'closure'
  | 'compliance' | 'registers'
  | 'reports' | 'grievances'
  | 'audit' | 'settings'
  | 'borrower';

// Inner component so it can use useRole hook (inside RoleProvider)
const AppInner: React.FC = () => {
  const { currentUser, setRole } = useRole();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [page, setPage] = useState<Page>('dashboard');
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [selectedMemberId, setSelectedMemberId] = useState<string | null>(null);
  const [selectedLoanAccountId, setSelectedLoanAccountId] = useState<string | null>(null);

  const handleLogin = (role: Role) => {
    setRole(role);
    setIsLoggedIn(true);
    // Route borrowers directly to their portal
    if (role === 'borrower') setPage('borrower');
    else setPage('dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setPage('dashboard');
  };

  if (!isLoggedIn) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  // Borrower gets their own portal layout (no sidebar/header chrome)
  if (currentUser.role === 'borrower') {
    return <BorrowerPortal onLogout={handleLogout} />;
  }

  const navigate = (target: Page, id?: string) => {
    setPage(target);
    if (target === 'applications/detail' && id) setSelectedApplicationId(id);
    if (target === 'members/profile' && id) setSelectedMemberId(id);
    if (target === 'loan-accounts/detail' && id) setSelectedLoanAccountId(id);
  };

  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return <Dashboard onNavigate={navigate} />;
      case 'tasks':
        return <TaskInbox onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'applications':
        return (
          <ApplicationList
            onNew={() => navigate('applications/new')}
            onSelect={id => navigate('applications/detail', id)}
          />
        );
      case 'applications/new':
        return <NewApplication onBack={() => navigate('applications')} />;
      case 'applications/detail':
        return (
          <ApplicationDetail
            applicationId={selectedApplicationId || 'app001'}
            onBack={() => navigate('applications')}
            onNavigateMember={id => navigate('members/profile', id)}
          />
        );
      case 'members':
        return <MemberDirectory onSelect={id => navigate('members/profile', id)} onBorrower360={id => navigate('members/borrower360', id)} />;
      case 'members/profile':
        return (
          <MemberProfile
            memberId={selectedMemberId || 'm001'}
            onBack={() => navigate('members')}
          />
        );
      case 'members/borrower360':
        return (
          <Borrower360
            memberId={selectedMemberId || 'm001'}
            onBack={() => navigate('members')}
            onOpenApplication={id => navigate('applications/detail', id)}
            onOpenLoanAccount={id => navigate('loan-accounts/detail', id)}
          />
        );
      case 'appraisal':
        return <AppraisalWorkbench onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'sanction':
        return <SanctionWorkbench onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'documentation':
        return <DocumentationHub onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'disbursement':
      case 'cfc':
        return <DisbursementHub onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'interest':
        return <InterestManagement />;
      case 'loan-accounts':
        return <LoanAccount360 loanAccountId={null} onSelect={id => navigate('loan-accounts/detail', id)} />;
      case 'loan-accounts/detail':
        return (
          <LoanAccount360
            loanAccountId={selectedLoanAccountId}
            onSelect={id => navigate('loan-accounts/detail', id)}
            onBack={() => navigate('loan-accounts')}
          />
        );
      case 'repayments':
        return <RepaymentsHub />;
      case 'monitoring':
        return <MonitoringDashboard onOpenLoan={id => navigate('loan-accounts/detail', id)} />;
      case 'defaults':
        return <DefaultRecoveryHub />;
      case 'closure':
        return <LoanClosureHub />;
      case 'compliance':
        return <ComplianceDashboard />;
      case 'registers':
      case 'audit':
      case 'grievances':
        return <RegistersHub />;
      case 'reports':
        return <ReportsMIS />;
      case 'settings':
        return <SettingsHub />;
      default:
        return <Dashboard onNavigate={navigate} />;
    }
  };

  const activePage = page.split('/')[0] as Page;

  return (
    <AppShell activePage={activePage} onNavigate={p => navigate(p as Page)} onLogout={handleLogout}>
      {renderPage()}
    </AppShell>
  );
};

const App: React.FC = () => (
  <RoleProvider>
    <AppInner />
    {import.meta.env.DEV && <Agentation endpoint="http://localhost:4747" />}
  </RoleProvider>
);

export default App;
