import { Link } from 'react-router-dom'
import { getDashboardStats } from '../auth/api'
import { useAuth } from '../auth/AuthContext'
import { useState, useEffect } from 'react'

type DashboardStats = {
  totais: {
    clientes: number
    agendamentos: number
    financeiro: number
  }
  financeiro: {
    pendente: number
    pago: number
  }
  proximos_agendamentos: {
    id: string
    cliente_nome: string
    data_hora: string
    status: string
  }[]
  receita_mensal: {
    mes: string
    valor: number
  }[]
  financeiro_por_status: {
    status: string
    valor: number
  }[]
}

export default function DashboardAnalyticsPage() {
  const auth = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getDashboardStats()
        setStats(data as DashboardStats)
      } catch (err: any) {
        setError(err?.detail || 'Erro ao carregar dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const formatCurrency = (value: number) => `R$ ${value.toFixed(2).replace('.', ',')}`

  const formatLocalDateTime = (iso: string) => new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

  const formatMes = (mes: string) => {
    const [year, month] = mes.split('-')
    return `${month}/${year}`
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error || !stats) return <div style={{ padding: 16, color: 'crimson' }}>{error || 'Dados indisponíveis'}</div>

  return (
    <div style={{ maxWidth: 1200, margin: '48px auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
        <h1>Dashboard Analítico</h1>
        <button onClick={() => auth.logout()}>Sair</button>
      </div>

      {/* Cards Totais */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 4 }}>
          <h3>Clientes Ativos</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold', margin: 0 }}>{stats.totais.clientes}</p>
        </div>
        <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 4 }}>
          <h3>Agendamentos</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold', margin: 0 }}>{stats.totais.agendamentos}</p>
        </div>
        <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 4 }}>
          <h3>Registros Financeiros</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold', margin: 0 }}>{stats.totais.financeiro}</p>
        </div>
        <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 4 }}>
          <h3>Recebido</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold', margin: 0, color: 'green' }}>{formatCurrency(stats.financeiro.pago)}</p>
        </div>
        <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 4 }}>
          <h3>A Receber</h3>
          <p style={{ fontSize: 24, fontWeight: 'bold', margin: 0, color: 'orange' }}>{formatCurrency(stats.financeiro.pendente)}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, marginBottom: 32 }}>
        {/* Próximos Agendamentos */}
        <div>
          <h2>Próximos Agendamentos (7 dias)</h2>
          {stats.proximos_agendamentos.length === 0 ? (
            <p>Nenhum agendamento próximo.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {stats.proximos_agendamentos.map((a) => (
                <li key={a.id} style={{ borderBottom: '1px solid #eee', padding: '8px 0' }}>
                  <strong>{a.cliente_nome}</strong> – {formatLocalDateTime(a.data_hora)} – {a.status}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Financeiro por Status */}
        <div>
          <h2>Financeiro por Status</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {stats.financeiro_por_status.map((item) => (
              <div key={item.status} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{item.status === 'pago' ? 'Pago' : 'Pendente'}</span>
                <strong>{formatCurrency(item.valor)}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Receita Mensal (últimos 6 meses) */}
      <div style={{ marginBottom: 32 }}>
        <h2>Receita Mensal (últimos 6 meses)</h2>
        {stats.receita_mensal.length === 0 ? (
          <p>Sem dados.</p>
        ) : (
          <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end' }}>
            {stats.receita_mensal.map((item) => {
              const maxValor = Math.max(...stats.receita_mensal.map((r) => r.valor)) || 1
              const percent = (item.valor / maxValor) * 100
              return (
                <div key={item.mes} style={{ textAlign: 'center' }}>
                  <div style={{ width: 60, height: 100, backgroundColor: '#e5e7eb', borderRadius: 4, position: 'relative' }}>
                    <div style={{ position: 'absolute', bottom: 0, width: '100%', backgroundColor: '#4f46e5', borderRadius: 4, height: `${Math.min(100, percent)}%` }} />
                  </div>
                  <div style={{ marginTop: 4 }}>{formatMes(item.mes)}</div>
                  <div style={{ fontSize: 12 }}>{formatCurrency(item.valor)}</div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Links Rápidos */}
      <div>
        <h2>Ações Rápidas</h2>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <Link to="/clientes">Gerenciar Clientes</Link>
          <Link to="/agendamentos">Gerenciar Agendamentos</Link>
          <Link to="/financeiro">Gerenciar Financeiro</Link>
          <Link to="/notificacoes">Notificações</Link>
        </div>
      </div>
    </div>
  )
}
