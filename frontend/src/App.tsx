import AppRoutes from './routes'
import { useAuth } from './auth/AuthContext'
import { useInactivityLogout } from './auth/useInactivityLogout'

function App() {
  const auth = useAuth()

  useInactivityLogout({
    enabled: Boolean(auth.accessToken),
    timeoutMs: 30 * 60 * 1000,
    onTimeout: () => {
      auth.logout()
    },
  })

  return <AppRoutes />
}

export default App
