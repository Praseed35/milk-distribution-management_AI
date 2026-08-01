import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./providers/AuthProvider";
import { QueryProvider } from "./providers/QueryProvider";
import ProtectedRoute from "./components/guards/ProtectedRoute";
import RoleGuard from "./components/guards/RoleGuard";

import AppLayout from "./components/layout/AppLayout";
import LoginPage from "./pages/LoginPage";
import ChangePasswordPage from "./pages/ChangePasswordPage";
import DashboardPage from "./pages/DashboardPage";
import NotFoundPage from "./pages/NotFoundPage";
import RouteListPage from "./pages/routes/RouteListPage";
import RouteFormPage from "./pages/routes/RouteFormPage";
import CustomerListPage from "./pages/customers/CustomerListPage";
import CustomerFormPage from "./pages/customers/CustomerFormPage";
import CustomerDetailPage from "./pages/customers/CustomerDetailPage";
import MilkTypeListPage from "./pages/milk-types/MilkTypeListPage";
import MilkTypeFormPage from "./pages/milk-types/MilkTypeFormPage";
import EmployeeListPage from "./pages/employees/EmployeeListPage";
import EmployeeFormPage from "./pages/employees/EmployeeFormPage";
import EmployeeCredentialsPage from "./pages/employees/EmployeeCredentialsPage";
import UserListPage from "./pages/users/UserListPage";
import UserCreatePage from "./pages/users/UserCreatePage";
import SubscriptionListPage from "./pages/subscriptions/SubscriptionListPage";
import SubscriptionFormPage from "./pages/subscriptions/SubscriptionFormPage";
import ExceptionListPage from "./pages/delivery-exceptions/ExceptionListPage";
import ExceptionFormPage from "./pages/delivery-exceptions/ExceptionFormPage";
import TokenIdentityListPage from "./pages/token-books/TokenIdentityListPage";
import TokenIdentityFormPage from "./pages/token-books/TokenIdentityFormPage";
import TokenBookIssueListPage from "./pages/token-books/TokenBookIssueListPage";
import TokenBookIssueFormPage from "./pages/token-books/TokenBookIssueFormPage";
import TokenBookPaymentListPage from "./pages/token-books/TokenBookPaymentListPage";
import TokenBookPaymentFormPage from "./pages/token-books/TokenBookPaymentFormPage";
import SessionListPage from "./pages/delivery/SessionListPage";
import SessionCreatePage from "./pages/delivery/SessionCreatePage";
import SessionDetailPage from "./pages/delivery/SessionDetailPage";
import DeliveryEditPage from "./pages/delivery/DeliveryEditPage";
import PaymentListPage from "./pages/payments/PaymentListPage";
import PaymentFormPage from "./pages/payments/PaymentFormPage";
import BillListPage from "./pages/payments/BillListPage";
import BillGeneratePage from "./pages/payments/BillGeneratePage";
import OutstandingPage from "./pages/payments/OutstandingPage";
import BillDetailPage from "./pages/payments/BillDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <QueryProvider>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="change-password" element={<ChangePasswordPage />} />
              <Route
                path="routes"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <RouteListPage />
                  </RoleGuard>
                }
              />
              <Route
                path="routes/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <RouteFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="routes/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <RouteFormPage />
                  </RoleGuard>
                }
              />
              <Route path="customers" element={<CustomerListPage />} />
              <Route path="customers/new" element={<CustomerFormPage />} />
              <Route path="customers/:id" element={<CustomerDetailPage />} />
              <Route path="customers/:id/edit" element={<CustomerFormPage />} />
              <Route path="milk-types" element={<MilkTypeListPage />} />
              <Route path="milk-types/new" element={<MilkTypeFormPage />} />
              <Route path="milk-types/:id/edit" element={<MilkTypeFormPage />} />
              <Route path="employees" element={<EmployeeListPage />} />
              <Route
                path="employees/new"
                element={
                  <RoleGuard roles={["OWNER"]}>
                    <EmployeeFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="employees/:id/edit"
                element={
                  <RoleGuard roles={["OWNER"]}>
                    <EmployeeFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="employees/:id/credentials"
                element={
                  <RoleGuard roles={["OWNER"]}>
                    <EmployeeCredentialsPage />
                  </RoleGuard>
                }
              />
              <Route path="users" element={<UserListPage />} />
              <Route path="users/new" element={<UserCreatePage />} />
              <Route path="subscriptions" element={<SubscriptionListPage />} />
              <Route
                path="subscriptions/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <SubscriptionFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="subscriptions/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <SubscriptionFormPage />
                  </RoleGuard>
                }
              />
              <Route path="delivery-exceptions" element={<ExceptionListPage />} />
              <Route
                path="delivery-exceptions/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <ExceptionFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="delivery-exceptions/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <ExceptionFormPage />
                  </RoleGuard>
                }
              />
              <Route path="token-identities" element={<TokenIdentityListPage />} />
              <Route
                path="token-identities/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <TokenIdentityFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="token-identities/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <TokenIdentityFormPage />
                  </RoleGuard>
                }
              />
              <Route path="token-book-issues" element={<TokenBookIssueListPage />} />
              <Route
                path="token-book-issues/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <TokenBookIssueFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="token-book-issues/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <TokenBookIssueFormPage />
                  </RoleGuard>
                }
              />
              <Route path="token-book-payments" element={<TokenBookPaymentListPage />} />
              <Route
                path="token-book-payments/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <TokenBookPaymentFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="token-book-payments/:id/edit"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <TokenBookPaymentFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="delivery/sessions"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <SessionListPage />
                  </RoleGuard>
                }
              />
              <Route
                path="delivery/sessions/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <SessionCreatePage />
                  </RoleGuard>
                }
              />
              <Route
                path="delivery/sessions/:id"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}>
                    <SessionDetailPage />
                  </RoleGuard>
                }
              />
              <Route
                path="delivery/sessions/:id/edit"
                element={
                  <RoleGuard roles={["OWNER"]}>
                    <DeliveryEditPage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <PaymentListPage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments/new"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <PaymentFormPage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments/bills"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <BillListPage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments/bills/generate"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <BillGeneratePage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments/bills/:id"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <BillDetailPage />
                  </RoleGuard>
                }
              />
              <Route
                path="payments/outstanding"
                element={
                  <RoleGuard roles={["OWNER", "ADMIN"]}>
                    <OutstandingPage />
                  </RoleGuard>
                }
              />
            </Route>
            <Route path="404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </AuthProvider>
      </QueryProvider>
    </BrowserRouter>
  );
}
