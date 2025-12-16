import { useNavigate, useParams } from 'react-router-dom'
import { getClientes, updateCliente } from '../auth/api'
import { useEffect, useState } from 'react'

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

export default function ClienteEditPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [cliente, setCliente] = useState<Cliente | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!id) return
    const fetch = async () => {
      try {
        const list = await getClientes()
        const found = (Array.isArray(list) ? list : (list.results || [])).find((c: Cliente) => c.id === id)
        if (!found) throw new Error('Cliente não encontrado')
        setCliente(found)
      } catch (err: any) {
        setError(err?.detail || 'Erro ao carregar cliente')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [id])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!id || !cliente) return
    setSubmitting(true)
    const form = e.currentTarget
    const data = {
      nome: (form.nome as HTMLInputElement).value,
      email: (form.email as HTMLInputElement).value || undefined,
      telefone: (form.telefone as HTMLInputElement).value || undefined,
      endereco: (form.endereco as HTMLTextAreaElement).value || undefined,
      tipo_piscina: (form.tipo_piscina as HTMLSelectElement).value as 'residencial' | 'comercial',
    }
    try {
      await updateCliente(id, data)
      navigate('/clientes')
    } catch (err: any) {
      alert(err?.detail || 'Erro ao atualizar cliente')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div style={{ padding: 16 }}>Carregando…</div>
  if (error || !cliente) return <div style={{ padding: 16, color: 'crimson' }}>{error || 'Cliente não encontrado'}</div>

  return (
    <div style={{ maxWidth: 640, margin: '48px auto', padding: 16 }}>
      <h1>Editar Cliente</h1>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
        <label>
          Nome *
          <input name="nome" defaultValue={cliente.nome} required style={{ width: '100%' }} />
        </label>
        <label>
          Email
          <input name="email" type="email" defaultValue={cliente.email || ''} style={{ width: '100%' }} />
        </label>
        <label>
          Telefone
          <input name="telefone" defaultValue={cliente.telefone || ''} style={{ width: '100%' }} />
        </label>
        <label>
          Endereço
          <textarea name="endereco" rows={2} defaultValue={cliente.endereco || ''} style={{ width: '100%' }} />
        </label>
        <label>
          Tipo de Piscina
          <select name="tipo_piscina" defaultValue={cliente.tipo_piscina} style={{ width: '100%' }}>
            <option value="residencial">Residencial</option>
            <option value="comercial">Comercial</option>
          </select>
        </label>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Salvando…' : 'Salvar'}
          </button>
          <button type="button" onClick={() => navigate('/clientes')}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}
