import { Link } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

export default function DashboardPage() {
  const auth = useAuth()

  return (
    <div style={{ maxWidth: 720, margin: '48px auto', padding: 16 }}>
      <h1>Dashboard</h1>
      <p>
        Logado como <strong>{auth.user?.nome || auth.user?.email}</strong>
      </p>

      <button onClick={() => auth.logout()}>Sair</button>

      <hr />
      <h2>Clientes</h2>
      <p>
        <Link to="/clientes">Gerenciar clientes</Link>
      </p>

      <h2>Agendamentos</h2>
      <p>
        <Link to="/agendamentos">Gerenciar agendamentos</Link>
      </p>

      <h2>Financeiro</h2>
      <p>
        <Link to="/financeiro">Gerenciar financeiro</Link>
      </p>
    </div>
  )
}
