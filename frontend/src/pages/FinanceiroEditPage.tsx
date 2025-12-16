import { useNavigate, useParams } from 'react-router-dom'
import { getFinanceiro, updateFinanceiro } from '../auth/api'
import { useEffect, useState } from 'react'

type Financeiro = {
  id: string
  cliente: string
  cliente_nome: string
  agendamento?: string
  tipo: 'servico' | 'produto' | 'multa' | 'outro'
  descricao?: string
  valor: string
  data_vencimento: string
  status: 'pendente' | 'pago'
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

type Cliente = {
  id: string
  nome: string
}

type Agendamento = {
  id: string
  cliente_nome: string
  data_hora: string
}

export default function FinanceiroEditPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [financeiro, setFinanceiro] = useState<Financeiro | null>(null)
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetch = async () => {
      if (!id) return
      try {
        const list = await getFinanceiro()
        const found = (Array.isArray(list) ? list : (list.results || [])).find((f: Financeiro) => f.id === id)
        if (!found) throw new Error('Registro financeiro não encontrado')
        setFinanceiro(found)
      } catch (err: any) {
        setError(err?.detail || 'Erro ao carregar financeiro')
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

  useEffect(() => {
    const fetchAgendamentos = async () => {
      try {
        const data = await (await import('../auth/api')).getAgendamentos()
        const items = Array.isArray(data) ? data : (data.results || [])
        setAgendamentos(items)
      } catch (err: any) {
        console.error('Erro ao carregar agendamentos', err)
      }
    }
    fetchAgendamentos()
  }, [])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!id || !financeiro) return
    setSubmitting(true)
    const form = e.currentTarget
    const data = {
      cliente: (form.cliente as HTMLSelectElement).value,
      agendamento: (form.agendamento as HTMLSelectElement).value || undefined,
      tipo: (form.tipo as HTMLSelectElement).value as 'servico' | 'produto' | 'multa' | 'outro',
      descricao: (form.descricao as HTMLInputElement).value || undefined,
      valor: parseFloat((form.valor as HTMLInputElement).value),
      data_vencimento: (form.data_vencimento as HTMLInputElement).value,
      status: (form.status as HTMLSelectElement).value as 'pendente' | 'pago',
    }
    try {
      await updateFinanceiro(id, data)
      navigate('/financeiro')
    } catch (err: any) {
      alert(err?.detail || 'Erro ao atualizar financeiro')
    } finally {
      setSubmitting(false)
    }
  }

  const formatLocalDate = (iso: string) => {
    const d = new Date(iso)
    return d.toISOString().slice(0, 10)
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error || !financeiro) return <div style={{ padding: 16, color: 'crimson' }}>{error || 'Registro financeiro não encontrado'}</div>

  return (
    <div style={{ maxWidth: 640, margin: '48px auto', padding: 16 }}>
      <h1>Editar Registro Financeiro</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
        <label>
          Cliente *
          <select name="cliente" defaultValue={financeiro.cliente} required style={{ width: '100%' }}>
            <option value="">Selecione um cliente</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome}
              </option>
            ))}
          </select>
        </label>
        <label>
          Agendamento (opcional)
          <select name="agendamento" defaultValue={financeiro.agendamento || ''} style={{ width: '100%' }}>
            <option value="">Selecione um agendamento</option>
            {agendamentos.map((a) => (
              <option key={a.id} value={a.id}>
                {a.cliente_nome} - {new Date(a.data_hora).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tipo *
          <select name="tipo" defaultValue={financeiro.tipo} required style={{ width: '100%' }}>
            <option value="servico">Serviço</option>
            <option value="produto">Produto</option>
            <option value="multa">Multa</option>
            <option value="outro">Outro</option>
          </select>
        </label>
        <label>
          Descrição
          <input name="descricao" defaultValue={financeiro.descricao || ''} style={{ width: '100%' }} />
        </label>
        <label>
          Valor (R$) *
          <input name="valor" type="number" step="0.01" min="0" defaultValue={financeiro.valor} required style={{ width: '100%' }} />
        </label>
        <label>
          Data de Vencimento *
          <input name="data_vencimento" type="date" defaultValue={formatLocalDate(financeiro.data_vencimento)} required style={{ width: '100%' }} />
        </label>
        <label>
          Status
          <select name="status" defaultValue={financeiro.status} style={{ width: '100%' }}>
            <option value="pendente">Pendente</option>
            <option value="pago">Pago</option>
          </select>
        </label>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Salvando…' : 'Salvar'}
          </button>
          <button type="button" onClick={() => navigate('/financeiro')}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}
