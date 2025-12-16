import { getNotificacoes, marcarNotificacaoComoLida, marcarTodasNotificacoesComoLidas } from '../auth/api'
import { useAuth } from '../auth/AuthContext'
import { useState, useEffect } from 'react'

type Notificacao = {
  id: string
  tipo: string
  titulo: string
  mensagem: string
  lida: boolean
  criado_em: string
  agendamento_id?: string
  financeiro_id?: string
}

export default function NotificacoesPage() {
  const auth = useAuth()
  const [notificacoes, setNotificacoes] = useState<Notificacao[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filtro, setFiltro] = useState<'todas' | 'nao-lidas'>('nao-lidas')

  useEffect(() => {
    const fetch = async () => {
      try {
        const params = filtro === 'nao-lidas' ? { lida: 'false' } : {}
        const data = await getNotificacoes(params)
        setNotificacoes(data.results || data)
      } catch (err: any) {
        setError(err?.detail || 'Erro ao carregar notificações')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [filtro])

  const handleMarcarComoLida = async (id: string) => {
    try {
      await marcarNotificacaoComoLida(id)
      setNotificacoes((prev) => prev.map((n) => (n.id === id ? { ...n, lida: true } : n)))
    } catch (err: any) {
      alert(err?.detail || 'Erro ao marcar como lida')
    }
  }

  const handleMarcarTodasComoLidas = async () => {
    try {
      await marcarTodasNotificacoesComoLidas()
      setNotificacoes((prev) => prev.map((n) => ({ ...n, lida: true })))
    } catch (err: any) {
      alert(err?.detail || 'Erro ao marcar todas como lidas')
    }
  }

  const formatLocalDateTime = (iso: string) => new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

  const naoLidasCount = notificacoes.filter((n) => !n.lida).length

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error) return <div style={{ padding: 16, color: 'crimson' }}>{error}</div>

  return (
    <div style={{ maxWidth: 960, margin: '48px auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Notificações</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setFiltro(filtro === 'todas' ? 'nao-lidas' : 'todas')}>
            {filtro === 'todas' ? 'Não Lidas' : 'Todas'}
          </button>
          {naoLidasCount > 0 && (
            <button onClick={handleMarcarTodasComoLidas}>Marcar Todas como Lidas</button>
          )}
        </div>
      </div>

      {notificacoes.length === 0 ? (
        <p>Nenhuma notificação.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {notificacoes.map((n) => (
            <li
              key={n.id}
              style={{
                border: n.lida ? '1px solid #ddd' : '1px solid #4f46e5',
                backgroundColor: n.lida ? '#f9f9f9' : '#f0f9ff',
                padding: 16,
                borderRadius: 4,
                marginBottom: 8,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <strong>{n.titulo}</strong>
                  <p style={{ margin: '4px 0' }}>{n.mensagem}</p>
                  <small style={{ color: '#666' }}>{formatLocalDateTime(n.criado_em)}</small>
                </div>
                {!n.lida && (
                  <button
                    onClick={() => handleMarcarComoLida(n.id)}
                    style={{ marginLeft: 12, padding: '4px 8px' }}
                  >
                    Marcar como lida
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
