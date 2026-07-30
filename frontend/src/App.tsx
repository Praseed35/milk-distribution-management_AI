import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./providers/AuthProvider";
import { QueryProvider } from "./providers/QueryProvider";
import ProtectedRoute from "./components/guards/ProtectedRoute";

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
              <Route path="routes" element={<RouteListPage />} />
              <Route path="routes/new" element={<RouteFormPage />} />
              <Route path="routes/:id/edit" element={<RouteFormPage />} />
              <Route path="customers" element={<CustomerListPage />} />
              <Route path="customers/new" element={<CustomerFormPage />} />
              <Route path="customers/:id" element={<CustomerDetailPage />} />
              <Route path="customers/:id/edit" element={<CustomerFormPage />} />
              <Route path="milk-types" element={<MilkTypeListPage />} />
              <Route path="milk-types/new" element={<MilkTypeFormPage />} />
              <Route path="milk-types/:id/edit" element={<MilkTypeFormPage />} />
              <Route path="employees" element={<EmployeeListPage />} />
              <Route path="employees/new" element={<EmployeeFormPage />} />
              <Route path="employees/:id/edit" element={<EmployeeFormPage />} />
              <Route path="employees/:id/credentials" element={<EmployeeCredentialsPage />} />
              <Route path="users" element={<UserListPage />} />
              <Route path="users/new" element={<UserCreatePage />} />
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
