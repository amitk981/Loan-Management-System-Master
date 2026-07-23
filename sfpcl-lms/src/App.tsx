import React, { useState, useEffect } from 'react';
import { Agentation } from 'agentation';
import { RoleProvider, useRole } from './contexts/RoleContext';
import { Role } from './types';
import {
  AuthSessionError,
  DEMO_AUTH_ENABLED,
  loginAndLoadCurrentUser,
  logoutSession,
  portalLoginAndLoadCurrentUser,
  restoreCurrentUserFromStoredSession,
} from './services/authSession';
import { Page, resolveNavigationAttempt } from './services/navigationPermissions';
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
import CompletenessWorkbench from './pages/applications/CompletenessWorkbench';
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
import AuditorEpic011View from './pages/compliance/AuditorEpic011View';
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
import TracerBullet from './pages/tracer/TracerBullet';
import AdminUsers from './pages/admin/AdminUsers';

export type { Page } from './services/navigationPermissions';

type AuthView = 'staff' | 'memberLogin' | 'memberActivation' | 'memberForgot';

// Inner component so it can use useRole hook (inside RoleProvider)
const AppInner: React.FC = () => {
  const { currentUser, setRole, setBackendUser, clearUser, can } = useRole();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSessionLoading, setIsSessionLoading] = useState(true);
  const [isSubmittingLogin, setIsSubmittingLogin] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [page, setPage] = useState<Page>('dashboard');
  const [selectedApplicationId, setSelectedApplicationId] = useState<string | null>(null);
  const [selectedMemberId, setSelectedMemberId] = useState<string | null>(null);
  const [selectedLoanAccountId, setSelectedLoanAccountId] = useState<string | null>(null);
  const [authView, setAuthView] = useState<AuthView>('staff');
  const [blockedPage, setBlockedPage] = useState<Page | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let cancelled = false;

    restoreCurrentUserFromStoredSession()
      .then(user => {
        if (cancelled) return;
        if (user) {
          setBackendUser(user);
          setIsLoggedIn(true);
          setPage('dashboard');
        }
      })
      .catch(error => {
        if (cancelled) return;
        setLoginError(sessionErrorMessage(error));
        setIsLoggedIn(false);
      })
      .finally(() => {
        if (!cancelled) setIsSessionLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [setBackendUser]);

  const handleStaffLogin = async (credentials: { email: string; password: string }) => {
    setIsSubmittingLogin(true);
    setLoginError('');
    try {
      const backendUser = await loginAndLoadCurrentUser(credentials);
      setBackendUser(backendUser);
      setIsLoggedIn(true);
      setPage('dashboard');
      setBlockedPage(null);
    } catch (error) {
      setIsLoggedIn(false);
      setLoginError(sessionErrorMessage(error));
    } finally {
      setIsSubmittingLogin(false);
    }
  };

  const handleMemberLogin = async (credentials: { identifier: string; password: string }) => {
    setIsSubmittingLogin(true);
    setLoginError('');
    try {
      const backendUser = await portalLoginAndLoadCurrentUser(credentials);
      setBackendUser(backendUser);
      setIsLoggedIn(true);
      setPage('borrower');
      setBlockedPage(null);
    } catch (error) {
      setIsLoggedIn(false);
      setLoginError(sessionErrorMessage(error));
    } finally {
      setIsSubmittingLogin(false);
    }
  };

  const handleDemoLogin = (role: Role) => {
    setRole(role);
    setIsLoggedIn(true);
    setLoginError('');
    // Route borrowers directly to their portal
    if (role === 'borrower') setPage('borrower');
    else setPage('dashboard');
  };

  const handleLogout = async () => {
    if (currentUser.isBackendSession) {
      try {
        await logoutSession();
      } catch {
        // Local session is cleared even if the network logout fails.
      }
    }
    clearUser();
    setIsLoggedIn(false);
    setPage('dashboard');
    setAuthView('staff');
    setLoginError('');
  };

  if (!isLoggedIn) {
    if (authView === 'memberLogin') {
      return (
        <MP00_Login
          onSubmitLogin={handleMemberLogin}
          onNavigateToActivation={() => setAuthView('memberActivation')}
          onNavigateToForgot={() => setAuthView('memberForgot')}
          onBackToStaffLogin={() => setAuthView('staff')}
          error={loginError}
          isSubmitting={isSubmittingLogin}
        />
      );
    }
    if (authView === 'memberActivation') {
      return (
        <MP01_Activation
          onBackToLogin={() => setAuthView('memberLogin')}
          onActivate={() => setAuthView('memberLogin')}
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
    return (
      <LoginScreen
        onLogin={handleStaffLogin}
        onDemoLogin={DEMO_AUTH_ENABLED ? handleDemoLogin : undefined}
        onOpenMemberPortal={() => setAuthView('memberLogin')}
        error={loginError}
        isSubmitting={isSubmittingLogin}
        isLoadingSession={isSessionLoading}
        showDemoRoleSelector={DEMO_AUTH_ENABLED}
      />
    );
  }

  // Borrower gets their own portal layout (no sidebar/header chrome)
  if (currentUser.role === 'borrower') {
    return <BorrowerPortal onLogout={handleLogout} />;
  }

  const navigate = (target: Page, id?: string) => {
    const attempt = resolveNavigationAttempt(target, can);
    if (!attempt.allowed) {
      setBlockedPage(attempt.blockedPage);
      setPage(attempt.page);
      return;
    }
    setBlockedPage(attempt.blockedPage);
    setPage(attempt.page);
    if (
      ['applications/detail', 'completeness', 'appraisal', 'sanction', 'documentation', 'disbursement', 'cfc'].includes(target) && id
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
        return (
          <GlobalSearchResults
            query={searchQuery}
            onNavigate={navigate}
            onQueryConsumed={() => setSearchQuery('')}
          />
        );
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
        return <NewApplication onBack={() => navigate('applications')} onNavigateTasks={() => navigate('tasks')} />;
      case 'applications/detail':
        return (
          <ApplicationDetail
            applicationId={selectedApplicationId || 'app001'}
            onBack={() => navigate('applications')}
            onNavigateMember={id => navigate('members/profile', id)}
            onNavigateAppraisal={id => navigate('appraisal', id)}
          />
        );
      case 'completeness':
        return (
          <CompletenessWorkbench
            initialSelectedId={selectedApplicationId || undefined}
            onOpenApplication={id => navigate('applications/detail', id)}
            onOpenAppraisal={id => navigate('appraisal', id)}
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
        return <MonitoringDashboard onOpenLoan={id => navigate('loan-accounts/detail', id)} onOpenDefault={() => navigate('defaults')} />;
      case 'defaults':
        return <DefaultRecoveryHub />;
      case 'closure':
        return <LoanClosureHub />;
      case 'compliance':
        return <ComplianceDashboard />;
      case 'registers':
        return <RegistersHub onOpenLoan={id => navigate('loan-accounts/detail', id)} onOpenApplication={id => navigate('applications/detail', id)} />;
      case 'audit':
        return currentUser.role === 'auditor' ? <AuditorEpic011View /> : <AuditArchiveHub />;
      case 'grievances':
        return <GrievancesHub />;
      case 'reports':
        return <ReportsMIS />;
      case 'settings':
        return <SettingsHub />;
      case 'admin-users':
        return <AdminUsers />;
      case 'profile':
        return <MyProfile />;
      case 'tracer':
        return <TracerBullet onSessionExpired={handleLogout} />;
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
            <p className="font-semibold">Access blocked for {currentUser.roleName}</p>
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

const sessionErrorMessage = (error: unknown): string => {
  if (error instanceof AuthSessionError) {
    if (error.code === 'INVALID_CREDENTIALS') return 'Invalid email or password.';
    if (error.code === 'TOKEN_EXPIRED' || error.code === 'INVALID_TOKEN') return 'Your session expired. Please sign in again.';
    if (error.code === 'AUTH_REQUIRED') return 'Please sign in to continue.';
    return error.message;
  }
  return 'Unable to reach the authentication service. Please try again.';
};

const App: React.FC = () => (
  <RoleProvider>
    <AppInner />
    {import.meta.env.DEV && <Agentation endpoint="http://localhost:4747" />}
  </RoleProvider>
);

export default App;
