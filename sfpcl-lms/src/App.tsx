import React, { useState } from 'react';
import { Agentation } from 'agentation';
import { Permission, RoleProvider, useRole } from './contexts/RoleContext';
import { Role } from './types';
import AppShell from './components/layout/AppShell';
import LoginScreen from './pages/auth/LoginScreen';
import BorrowerPortal from './pages/borrower/BorrowerPortal';
import MP00_Login from './pages/borrower/portal/auth/MP00_Login';
import MP01_Activation from './pages/borrower/portal/auth/MP01_Activation';
import MP02_ForgotPassword from './pages/borrower/portal/auth/MP02_ForgotPassword';

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
import PaymentAuthorisationHub from './pages/disbursement/PaymentAuthorisationHub';
import LoanAccount360 from './pages/loan-accounts/LoanAccount360';
import RepaymentsHub from './pages/repayments/RepaymentsHub';
import MonitoringDashboard from './pages/monitoring/MonitoringDashboard';
import ComplianceDashboard from './pages/compliance/ComplianceDashboard';
import GrievancesHub from './pages/compliance/GrievancesHub';
import AuditArchiveHub from './pages/compliance/AuditArchiveHub';
import RegistersHub from './pages/registers/RegistersHub';
import TaskInbox from './pages/tasks/TaskInbox';
import DefaultRecoveryHub from './pages/defaults/DefaultRecoveryHub';
import LoanClosureHub from './pages/closure/LoanClosureHub';
import InterestManagement from './pages/interest/InterestManagement';
import SettingsHub from './pages/settings/SettingsHub';
import ReportsMIS from './pages/reports/ReportsMIS';
import GlobalSearchResults from './pages/search/GlobalSearchResults';
import NotificationsCenter from './pages/notifications/NotificationsCenter';
import MyProfile from './pages/profile/MyProfile';

export type Page =
  | 'dashboard' | 'tasks'
  | 'search' | 'notifications'
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
  | 'audit' | 'settings' | 'profile'
  | 'borrower';

type AuthView = 'staff' | 'memberLogin' | 'memberActivation' | 'memberForgot';

const PAGE_PERMISSIONS: Partial<Record<Page, Permission>> = {
  tasks: 'view_applications',
  applications: 'view_applications',
  'applications/new': 'create_application',
  'applications/detail': 'view_applications',
  members: 'view_members',
  'members/profile': 'view_members',
  'members/borrower360': 'view_members',
  appraisal: 'do_appraisal',
  sanction: 'view_sanction',
  documentation: 'view_documentation',
  disbursement: 'initiate_disbursement',
  cfc: 'authorise_disbursement',
  interest: 'manage_interest',
  'loan-accounts': 'view_loan_accounts',
  'loan-accounts/detail': 'view_loan_accounts',
  repayments: 'post_repayment',
  monitoring: 'view_monitoring',
  defaults: 'manage_defaults',
  closure: 'manage_closure',
  compliance: 'view_compliance',
  registers: 'view_registers',
  reports: 'view_reports',
  grievances: 'view_compliance',
  audit: 'view_audit',
  settings: 'view_settings',
  borrower: 'view_own_loan',
};

// Inner component so it can use useRole hook (inside RoleProvider)
const AppInner: React.FC = () => {
  const { currentUser, setRole, can } = useRole();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [page, setPage] = useState<Page>('dashboard');
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [selectedMemberId, setSelectedMemberId] = useState<string | null>(null);
  const [selectedLoanAccountId, setSelectedLoanAccountId] = useState<string | null>(null);
  const [authView, setAuthView] = useState<AuthView>('staff');
  const [blockedPage, setBlockedPage] = useState<Page | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

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
    setAuthView('staff');
  };

  if (!isLoggedIn) {
    if (authView === 'memberLogin') {
      return (
        <MP00_Login
          onLogin={() => handleLogin('borrower')}
          onNavigateToActivation={() => setAuthView('memberActivation')}
          onNavigateToForgot={() => setAuthView('memberForgot')}
          onBackToStaffLogin={() => setAuthView('staff')}
        />
      );
    }
    if (authView === 'memberActivation') {
      return (
        <MP01_Activation
          onBackToLogin={() => setAuthView('memberLogin')}
          onActivate={() => handleLogin('borrower')}
        />
      );
    }
    if (authView === 'memberForgot') {
      return (
        <MP02_ForgotPassword
          onBackToLogin={() => setAuthView('memberLogin')}
          onResetComplete={() => setAuthView('memberLogin')}
        />
      );
    }
    return <LoginScreen onLogin={handleLogin} onOpenMemberPortal={() => setAuthView('memberLogin')} />;
  }

  // Borrower gets their own portal layout (no sidebar/header chrome)
  if (currentUser.role === 'borrower') {
    return <BorrowerPortal onLogout={handleLogout} />;
  }

  const navigate = (target: Page, id?: string) => {
    const requiredPermission = PAGE_PERMISSIONS[target];
    if (requiredPermission && !can(requiredPermission)) {
      setBlockedPage(target);
      setPage('dashboard');
      return;
    }
    setBlockedPage(null);
    setPage(target);
    if (
      ['applications/detail', 'appraisal', 'sanction', 'documentation', 'disbursement', 'cfc'].includes(target) && id
    ) {
      setSelectedApplicationId(id);
    }
    if (target === 'members/profile' && id) setSelectedMemberId(id);
    if (target === 'loan-accounts/detail' && id) setSelectedLoanAccountId(id);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    navigate('search');
  };

  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return <Dashboard onNavigate={navigate} />;
      case 'search':
        return <GlobalSearchResults query={searchQuery} onNavigate={navigate} />;
      case 'notifications':
        return <NotificationsCenter onNavigate={navigate} />;
      case 'tasks':
        return <TaskInbox onNavigate={navigate} />;
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
        return <AppraisalWorkbench onOpenApplication={id => navigate('applications/detail', id)} initialSelectedId={selectedApplicationId || undefined} />;
      case 'sanction':
        return <SanctionWorkbench onOpenApplication={id => navigate('applications/detail', id)} initialSelectedId={selectedApplicationId || undefined} />;
      case 'documentation':
        return <DocumentationHub onOpenApplication={id => navigate('applications/detail', id)} initialSelectedId={selectedApplicationId || undefined} />;
      case 'disbursement':
        return <DisbursementHub onOpenApplication={id => navigate('applications/detail', id)} initialSelectedId={selectedApplicationId || undefined} />;
      case 'cfc':
        return <PaymentAuthorisationHub onOpenApplication={id => navigate('applications/detail', id)} initialSelectedId={selectedApplicationId || undefined} />;
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
        return <RegistersHub />;
      case 'audit':
        return <AuditArchiveHub />;
      case 'grievances':
        return <GrievancesHub />;
      case 'reports':
        return <ReportsMIS />;
      case 'settings':
        return <SettingsHub />;
      case 'profile':
        return <MyProfile />;
      default:
        return <Dashboard onNavigate={navigate} />;
    }
  };

  const activePage = page.split('/')[0] as Page;

  return (
    <AppShell activePage={activePage} onNavigate={p => navigate(p as Page)} onSearch={handleSearch} onLogout={handleLogout}>
      {blockedPage && (
        <div className="px-6 pt-6">
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <p className="font-semibold">Access blocked for {currentUser.role.replace(/_/g, ' ')}</p>
            <p className="mt-0.5">
              The requested workspace ({blockedPage.replace(/\//g, ' / ')}) is hidden for this role and actions remain disabled unless the role has the required permission.
            </p>
          </div>
        </div>
      )}
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
