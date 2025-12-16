import { useNavigate, useParams } from 'react-router-dom'
import { getAgendamentos, updateAgendamento } from '../auth/api'
import { useEffect, useState } from 'react'

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

export default function AgendamentoEditPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [agendamento, setAgendamento] = useState<Agendamento | null>(null)
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetch = async () => {
      if (!id) return
      try {
        const list = await getAgendamentos()
        const found = (Array.isArray(list) ? list : (list.results || [])).find((a: Agendamento) => a.id === id)
        if (!found) throw new Error('Agendamento não encontrado')
        setAgendamento(found)
      } catch (err: any) {
        setError(err?.detail || 'Erro ao carregar agendamento')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [id])

  useEffect(() => {
    const fetchClientes = async () => {
      try {
        const data = await (await import('../auth/api')).getClientes()
        const items = Array.isArray(data) ? data : (data.results || [])
        setClientes(items)
      } catch (err: any) {
        console.error('Erro ao carregar clientes', err)
      }
    }
    fetchClientes()
  }, [])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!id || !agendamento) return
    setSubmitting(true)
    const form = e.currentTarget
    const data = {
      cliente: (form.cliente as HTMLSelectElement).value,
      data_hora: (form.data_hora as HTMLInputElement).value,
      status: (form.status as HTMLSelectElement).value as 'pendente' | 'confirmado' | 'cancelado' | 'realizado',
      observacoes: (form.observacoes as HTMLTextAreaElement).value || undefined,
    }
    try {
      await updateAgendamento(id, data)
      navigate('/agendamentos')
    } catch (err: any) {
      alert(err?.detail || 'Erro ao atualizar agendamento')
    } finally {
      setSubmitting(false)
    }
  }

  const formatLocalDateTime = (iso: string) => {
    const d = new Date(iso)
    return d.toISOString().slice(0, 16)
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error || !agendamento) return <div style={{ padding: 16, color: 'crimson' }}>{error || 'Agendamento não encontrado'}</div>

  return (
    <div style={{ maxWidth: 640, margin: '48px auto', padding: 16 }}>
      <h1>Editar Agendamento</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
        <label>
          Cliente *
          <select name="cliente" defaultValue={agendamento.cliente} required style={{ width: '100%' }}>
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
          <input name="data_hora" type="datetime-local" defaultValue={formatLocalDateTime(agendamento.data_hora)} required style={{ width: '100%' }} />
        </label>
        <label>
          Status
          <select name="status" defaultValue={agendamento.status} style={{ width: '100%' }}>
            <option value="pendente">Pendente</option>
            <option value="confirmado">Confirmado</option>
            <option value="cancelado">Cancelado</option>
            <option value="realizado">Realizado</option>
          </select>
        </label>
        <label>
          Observações
          <textarea name="observacoes" rows={2} defaultValue={agendamento.observacoes || ''} style={{ width: '100%' }} />
        </label>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Salvando…' : 'Salvar'}
          </button>
          <button type="button" onClick={() => navigate('/agendamentos')}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}
