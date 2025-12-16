import { Link } from 'react-router-dom'
import { createCliente, getClientes, softDeleteCliente, exportClientesCSV, exportClientesPDF } from '../auth/api'
import { useAuth } from '../auth/AuthContext'
import { useState, useEffect } from 'react'

type Cliente = {
  id: string
  nome: string
  email?: string
  telefone?: string
  endereco?: string
  tipo_piscina: 'residencial' | 'comercial'
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export default function ClientesPage() {
  const auth = useAuth()
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  const fetchClientes = async () => {
    try {
      const data = await getClientes({ ativo: true })
      const items = Array.isArray(data) ? data : (data.results || [])
      setClientes(items)
    } catch (err: any) {
      setError(err?.detail || 'Erro ao carregar clientes')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchClientes()
  }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja desativar este cliente?')) return
    try {
      await softDeleteCliente(id)
      await fetchClientes()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao desativar cliente')
    }
  }

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const data = {
      nome: (form.nome as HTMLInputElement).value,
      email: (form.email as HTMLInputElement).value || undefined,
      telefone: (form.telefone as HTMLInputElement).value || undefined,
      endereco: (form.endereco as HTMLTextAreaElement).value || undefined,
      tipo_piscina: (form.tipo_piscina as HTMLSelectElement).value as 'residencial' | 'comercial',
    }
    try {
      await createCliente(data)
      setShowForm(false)
      await fetchClientes()
    } catch (err: any) {
      alert(err?.detail || 'Erro ao criar cliente')
    }
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error) return <div style={{ padding: 16, color: 'crimson' }}>{error}</div>

  return (
    <div style={{ maxWidth: 960, margin: '48px auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Clientes</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setShowForm(true)}>+ Novo Cliente</button>
          <button onClick={async () => {
            try {
              await exportClientesCSV()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar CSV')
            }
          }}>Exportar CSV</button>
          <button onClick={async () => {
            try {
              await exportClientesPDF()
            } catch (err: any) {
              alert(err?.message || 'Erro ao exportar PDF')
            }
          }}>Exportar PDF</button>
        </div>
      </div>

      {showForm && (
        <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 4, marginBottom: 24 }}>
          <h2>Novo Cliente</h2>
          <form onSubmit={handleCreate} style={{ display: 'grid', gap: 12 }}>
            <label>
              Nome *
              <input name="nome" required style={{ width: '100%' }} />
            </label>
            <label>
              Email
              <input name="email" type="email" style={{ width: '100%' }} />
            </label>
            <label>
              Telefone
              <input name="telefone" style={{ width: '100%' }} />
            </label>
            <label>
              Endereço
              <textarea name="endereco" rows={2} style={{ width: '100%' }} />
            </label>
            <label>
              Tipo de Piscina
              <select name="tipo_piscina" style={{ width: '100%' }}>
                <option value="residencial">Residencial</option>
                <option value="comercial">Comercial</option>
              </select>
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="submit">Salvar</button>
              <button type="button" onClick={() => setShowForm(false)}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {clientes.length === 0 ? (
        <p>Nenhum cliente cadastrado.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #ddd' }}>
              <th style={{ textAlign: 'left', padding: 8 }}>Nome</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Telefone</th>
              <th style={{ textAlign: 'left', padding: 8 }}>Tipo</th>
              <th style={{ textAlign: 'left', padding: 8 }}></th>
            </tr>
          </thead>
          <tbody>
            {clientes.map((c) => (
              <tr key={c.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 8 }}>{c.nome}</td>
                <td style={{ padding: 8 }}>{c.email || '-'}</td>
                <td style={{ padding: 8 }}>{c.telefone || '-'}</td>
                <td style={{ padding: 8 }}>{c.tipo_piscina}</td>
                <td style={{ padding: 8, display: 'flex', gap: 8 }}>
                  <Link to={`/clientes/${c.id}/editar`}>Editar</Link>
                  <button onClick={() => handleDelete(c.id)} style={{ background: 'none', border: 'none', color: 'crimson', cursor: 'pointer' }}>
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
