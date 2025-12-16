import { Link } from 'react-router-dom'
import { createFinanceiro, getFinanceiro, softDeleteFinanceiro, exportFinanceiroCSV, exportFinanceiroPDF } from '../auth/api'
import { useAuth } from '../auth/AuthContext'
import { useState, useEffect } from 'react'

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

export default function FinanceiroPage() {
  const auth = useAuth()
  const [financeiros, setFinanceiros] = useState<Financeiro[]>([])
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  const fetchFinanceiros = async () => {
    try {
      const data = await getFinanceiro()
      const items = Array.isArray(data) ? data : (data.results || [])
      setFinanceiros(items)
    } catch (err: any) {
      setError(err?.detail || 'Erro ao carregar financeiros')
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

  const fetchAgendamentos = async () => {
    try {
      const data = await (await import('../auth/api')).getAgendamentos()
      const items = Array.isArray(data) ? data : (data.results || [])
      setAgendamentos(items)
    } catch (err: any) {
      console.error('Erro ao carregar agendamentos', err)
    }
  }

  useEffect(() => {
    fetchFinanceiros()
    fetchClientes()
    fetchAgendamentos()
  }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja desativar este registro financeiro?')) return
    try {
      await softDeleteFinanceiro(id)
      await fetchFinanceiros()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao desativar financeiro')
    }
  }

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
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
      await createFinanceiro(data)
      setShowForm(false)
      await fetchFinanceiros()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao criar financeiro')
    }
  }

  const formatLocalDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR')
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error) return <div style={{ padding: 16, color: 'crimson' }}>{error}</div>

  return (
    <div style={{ maxWidth: 960, margin: '48px auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Financeiro</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setShowForm(true)}>+ Novo Registro</button>
          <button onClick={async () => {
            try {
              await exportFinanceiroCSV()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar CSV')
            }
          }}>Exportar CSV</button>
          <button onClick={async () => {
            try {
              await exportFinanceiroPDF()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar PDF')
            }
          }}>Exportar PDF</button>
        </div>
      </div>

      {showForm && (
        <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 4, marginBottom: 24 }}>
          <h2>Novo Registro Financeiro</h2>
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
              Agendamento (opcional)
              <select name="agendamento" style={{ width: '100%' }}>
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
              <select name="tipo" required style={{ width: '100%' }}>
                <option value="servico">Serviço</option>
                <option value="produto">Produto</option>
                <option value="multa">Multa</option>
                <option value="outro">Outro</option>
              </select>
            </label>
            <label>
              Descrição
              <input name="descricao" style={{ width: '100%' }} />
            </label>
            <label>
              Valor (R$) *
              <input name="valor" type="number" step="0.01" min="0" required style={{ width: '100%' }} />
            </label>
            <label>
              Data de Vencimento *
              <input name="data_vencimento" type="date" required style={{ width: '100%' }} />
            </label>
            <label>
              Status
              <select name="status" style={{ width: '100%' }}>
                <option value="pendente">Pendente</option>
                <option value="pago">Pago</option>
              </select>
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit">Salvar</button>
              <button type="button" onClick={() => setShowForm(false)}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {financeiros.length === 0 ? (
        <p>Nenhum registro financeiro cadastrado.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ddd' }}>
              <th style={{ textAlign: 'left', padding: 8 }}>Cliente</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Tipo</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Descrição</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Valor</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Vencimento</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Status</th>
              <th style={{ textAlign: 'left', padding: 8 }}></th>
            </tr>
          </thead>
          <tbody>
            {financeiros.map((f) => (
              <tr key={f.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 8 }}>{f.cliente_nome}</td>
                <td style={{ padding: 8 }}>{f.tipo}</td>
                <td style={{ padding: 8 }}>{f.descricao || '-'}</td>
                <td style={{ padding: 8 }}>R$ {Number(f.valor).toFixed(2)}</td>
                <td style={{ padding: 8 }}>{formatLocalDate(f.data_vencimento)}</td>
                <td style={{ padding: 8 }}>{f.status}</td>
                <td style={{ padding: 8, display: 'flex', gap: 8 }}>
                  <Link to={`/financeiro/${f.id}/editar`}>Editar</Link>
                  <button onClick={() => handleDelete(f.id)} style={{ background: 'none', border: 'none', color: 'crimson', cursor: 'pointer' }}>
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
