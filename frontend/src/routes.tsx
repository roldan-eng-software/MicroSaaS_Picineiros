import { Navigate, Route, Routes } from 'react-router-dom'

import { useAuth } from './auth/AuthContext'
import DashboardAnalyticsPage from './pages/DashboardAnalyticsPage'
import LoginPage from './pages/LoginPage'
import ClientesPage from './pages/ClientesPage'
import ClienteEditPage from './pages/ClienteEditPage'
import AgendamentosPage from './pages/AgendamentosPage'
import AgendamentoEditPage from './pages/AgendamentoEditPage'
import FinanceiroPage from './pages/FinanceiroPage'
import FinanceiroEditPage from './pages/FinanceiroEditPage'
import NotificacoesPage from './pages/NotificacoesPage'

function Protected({ children }: { children: React.ReactNode }) {
  const auth = useAuth()

  if (auth.loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (!auth.accessToken) return <Navigate to="/login" replace />

  return <>{children}</>
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <Protected>
            <DashboardAnalyticsPage />
          </Protected>
        }
      />
      <Route
        path="/clientes"
        element={
          <Protected>
            <ClientesPage />
          </Protected>
        }
      />
      <Route
        path="/clientes/:id/editar"
        element={
          <Protected>
            <ClienteEditPage />
          </Protected>
        }
      />
      <Route
        path="/agendamentos"
        element={
          <Protected>
            <AgendamentosPage />
          </Protected>
        }
      />
      <Route
        path="/agendamentos/:id/editar"
        element={
          <Protected>
            <AgendamentoEditPage />
          </Protected>
        }
      />
      <Route
        path="/financeiro"
        element={
          <Protected>
            <FinanceiroPage />
          </Protected>
        }
      />
      <Route
        path="/financeiro/:id/editar"
        element={
          <Protected>
            <FinanceiroEditPage />
          </Protected>
        }
      />
      <Route
        path="/notificacoes"
        element={
          <Protected>
            <NotificacoesPage />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
