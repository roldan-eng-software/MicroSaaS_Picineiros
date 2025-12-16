import { Link } from 'react-router-dom'
import { createAgendamento, getAgendamentos, softDeleteAgendamento, exportAgendamentosCSV, exportAgendamentosPDF } from '../auth/api'
import { useAuth } from '../auth/AuthContext'
import { useState, useEffect } from 'react'

type Agendamento = {
  id: string
  cliente: string
  cliente_nome: string
  data_hora: string
  status: 'pendente' | 'confirmado' | 'cancelado' | 'realizado'
  observacoes?: string
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

type Cliente = {
  id: string
  nome: string
}

export default function AgendamentosPage() {
  const auth = useAuth()
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([])
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  const fetchAgendamentos = async () => {
    try {
      const data = await getAgendamentos()
      const items = Array.isArray(data) ? data : (data.results || [])
      setAgendamentos(items)
    } catch (err: any) {
      setError(err?.detail || 'Erro ao carregar agendamentos')
    } finally {
      setLoading(false)
    }
  }

  const fetchClientes = async () => {
    try {
      const data = await (await import('../auth/api')).getClientes()
      const items = Array.isArray(data) ? data : (data.results || [])
      setClientes(items)
    } catch (err: any) {
      console.error('Erro ao carregar clientes', err)
    }
  }

  useEffect(() => {
    fetchAgendamentos()
    fetchClientes()
  }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja desativar este agendamento?')) return
    try {
      await softDeleteAgendamento(id)
      await fetchAgendamentos()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao desativar agendamento')
    }
  }

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const data = {
      cliente: (form.cliente as HTMLSelectElement).value,
      data_hora: (form.data_hora as HTMLInputElement).value,
      status: (form.status as HTMLSelectElement).value as 'pendente' | 'confirmado' | 'cancelado' | 'realizado',
      observacoes: (form.observacoes as HTMLTextAreaElement).value || undefined,
    }
    try {
      await createAgendamento(data)
      setShowForm(false)
      await fetchAgendamentos()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao criar agendamento')
    }
  }

  const formatLocalDateTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error) return <div style={{ padding: 16, color: 'crimson' }}>{error}</div>

  return (
    <div style={{ maxWidth: 960, margin: '48px auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Agendamentos</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setShowForm(true)}>+ Novo Agendamento</button>
          <button onClick={async () => {
            try {
              await exportAgendamentosCSV()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar CSV')
            }
          }}>Exportar CSV</button>
          <button onClick={async () => {
            try {
              await exportAgendamentosPDF()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar PDF')
            }
          }}>Exportar PDF</button>
        </div>
      </div>

      {showForm && (
        <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 4, marginBottom: 24 }}>
          <h2>Novo Agendamento</h2>
          <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12 }}>
            <label>
              Cliente *
              <select name="cliente" required style={{ width: '100%' }}>
                <option value="">Selecione um cliente</option>
                {clientes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nome}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Data e Hora *
              <input name="data_hora" type="datetime-local" required style={{ width: '100%' }} />
            </label>
            <label>
              Status
              <select name="status" style={{ width: '100%' }}>
                <option value="pendente">Pendente</option>
                <option value="confirmado">Confirmado</option>
                <option value="cancelado">Cancelado</option>
                <option value="realizado">Realizado</option>
              </select>
            </label>
            <label>
              Observações
              <textarea name="observacoes" rows={2} style={{ width: '100%' }} />
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit">Salvar</button>
              <button type="button" onClick={() => setShowForm(false)}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {agendamentos.length === 0 ? (
        <p>Nenhum agendamento cadastrado.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ddd' }}>
              <th style={{ textAlign: 'left', padding: 8 }}>Cliente</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Data/Hora</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Status</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Observações</th>
              <th style={{ textAlign: 'left', padding: 8 }}></th>
            </tr>
          </thead>
          <tbody>
            {agendamentos.map((a) => (
              <tr key={a.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 8 }}>{a.cliente_nome}</td>
                <td style={{ padding: 8 }}>{formatLocalDateTime(a.data_hora)}</td>
                <td style={{ padding: 8 }}>{a.status}</td>
                <td style={{ padding: 8 }}>{a.observacoes || '-'}</td>
                <td style={{ padding: 8, display: 'flex', gap: 8 }}>
                  <Link to={`/agendamentos/${a.id}/editar`}>Editar</Link>
                  <button onClick={() => handleDelete(a.id)} style={{ background: 'none', border: 'none', color: 'crimson', cursor: 'pointer' }}>
                    Desativar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
