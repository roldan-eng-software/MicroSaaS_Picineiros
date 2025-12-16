const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()!.split(';').shift() || null
  return null
}

export type ApiError = {
  status: number
  detail?: string
}

async function fetchCsrfToken(): Promise<string> {
  await fetch(`${API_BASE_URL}/api/auth/csrf/`, {
    method: 'GET',
    credentials: 'include',
  })

  const token = getCookie('csrftoken')
  if (!token) throw new Error('Missing csrftoken cookie')
  return token
}

async function refreshAccessToken(csrfToken: string): Promise<string> {
  const resp = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({}),
  })

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    const err: ApiError = { status: resp.status, detail: body?.detail }
    throw err
  }

  const data = (await resp.json()) as { access: string }
  return data.access
}

export async function apiFetch(inputPath: string, init: RequestInit = {}): Promise<Response> {
  const url = inputPath.startsWith('http') ? inputPath : `${API_BASE_URL}${inputPath}`

  const attempt = async (): Promise<Response> => {
    const access = localStorage.getItem('access_token')

    const headers = new Headers(init.headers || {})
    if (!headers.has('Content-Type') && init.body) headers.set('Content-Type', 'application/json')
    if (access) headers.set('Authorization', `Bearer ${access}`)

    return fetch(url, {
      ...init,
      headers,
      credentials: 'include',
    })
  }

  let resp = await attempt()
  if (resp.status !== 401) return resp

  const csrf = await fetchCsrfToken()
  const newAccess = await refreshAccessToken(csrf)
  localStorage.setItem('access_token', newAccess)

  resp = await attempt()
  return resp
}

export async function apiJson<T>(inputPath: string, init: RequestInit = {}): Promise<T> {
  const resp = await apiFetch(inputPath, init)
  const data = await resp.json().catch(() => ({}))

  if (!resp.ok) {
    const err: ApiError = { status: resp.status, detail: (data as any)?.detail }
    throw err
  }

  return data as T
}

export async function login(email: string, password: string): Promise<string> {
  const csrf = await fetchCsrfToken()

  const resp = await fetch(`${API_BASE_URL}/api/auth/login/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf,
    },
    body: JSON.stringify({ email, password }),
  })

  const data = await resp.json().catch(() => ({}))
  if (!resp.ok) {
    const err: ApiError = { status: resp.status, detail: (data as any)?.detail }
    throw err
  }

  return (data as any).access as string
}

export async function logout(): Promise<void> {
  const csrf = await fetchCsrfToken()

  await fetch(`${API_BASE_URL}/api/auth/logout/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf,
    },
    body: JSON.stringify({}),
  })
}

export async function getMe(): Promise<{ id: string; email: string; nome: string; telefone: string; is_active: boolean }>
{
  return apiJson('/api/auth/me/')
}

export async function initFromRefresh(): Promise<string> {
  const csrf = await fetchCsrfToken()
  return refreshAccessToken(csrf)
}

export async function getClientes(params?: { ativo?: boolean; tipo_piscina?: 'residencial' | 'comercial' }) {
  const q = params ? new URLSearchParams(params as any).toString() : ''
  return apiJson(`/api/clientes/?${q}`)
}

export async function createCliente(data: {
  nome: string
  email?: string
  telefone?: string
  endereco?: string
  tipo_piscina: 'residencial' | 'comercial'
}) {
  return apiJson('/api/clientes/', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateCliente(id: string, data: {
  nome?: string
  email?: string
  telefone?: string
  endereco?: string
  tipo_piscina?: 'residencial' | 'comercial'
}) {
  return apiJson(`/api/clientes/${id}/`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function softDeleteCliente(id: string) {
  return apiJson(`/api/clientes/${id}/`, { method: 'DELETE' })
}

export async function getAgendamentos(params?: { status?: 'pendente' | 'confirmado' | 'cancelado' | 'realizado'; cliente?: string }) {
  const q = params ? new URLSearchParams(params as any).toString() : ''
  return apiJson(`/api/agendamentos/?${q}`)
}

export async function createAgendamento(data: {
  cliente: string
  data_hora: string
  status?: 'pendente' | 'confirmado' | 'cancelado' | 'realizado'
  observacoes?: string
}) {
  return apiJson('/api/agendamentos/', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateAgendamento(id: string, data: {
  cliente?: string
  data_hora?: string
  status?: 'pendente' | 'confirmado' | 'cancelado' | 'realizado'
  observacoes?: string
}) {
  return apiJson(`/api/agendamentos/${id}/`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function softDeleteAgendamento(id: string) {
  return apiJson(`/api/agendamentos/${id}/`, { method: 'DELETE' })
}

export async function getFinanceiro(params?: { status?: 'pendente' | 'pago'; tipo?: 'servico' | 'produto' | 'multa' | 'outro'; cliente?: string }) {
  const q = params ? new URLSearchParams(params as any).toString() : ''
  return apiJson(`/api/financeiro/?${q}`)
}

export async function createFinanceiro(data: {
  cliente: string
  agendamento?: string
  tipo: 'servico' | 'produto' | 'multa' | 'outro'
  descricao?: string
  valor: number
  data_vencimento: string
  status?: 'pendente' | 'pago'
}) {
  return apiJson('/api/financeiro/', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateFinanceiro(id: string, data: {
  cliente?: string
  agendamento?: string
  tipo?: 'servico' | 'produto' | 'multa' | 'outro'
  descricao?: string
  valor?: number
  data_vencimento?: string
  status?: 'pendente' | 'pago'
}) {
  return apiJson(`/api/financeiro/${id}/`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function softDeleteFinanceiro(id: string) {
  return apiJson(`/api/financeiro/${id}/`, { method: 'DELETE' })
}

export async function getDashboardStats() {
  return apiJson('/api/dashboard/stats/')
}

export async function exportClientesCSV() {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/relatorios/clientes/csv/`, {
    credentials: 'include',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  })
  if (!response.ok) throw new Error('Erro ao exportar')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'clientes.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

export async function exportClientesPDF() {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/relatorios/clientes/pdf/`, {
    credentials: 'include',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  })
  if (!response.ok) throw new Error('Erro ao exportar')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'clientes.pdf'
  a.click()
  window.URL.revokeObjectURL(url)
}

export async function exportAgendamentosCSV() {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/relatorios/agendamentos/csv/`, {
    credentials: 'include',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  })
  if (!response.ok) throw new Error('Erro ao exportar')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'agendamentos.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

export async function exportAgendamentosPDF() {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/relatorios/agendamentos/pdf/`, {
    credentials: 'include',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  })
  if (!response.ok) throw new Error('Erro ao exportar')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'agendamentos.pdf'
  a.click()
  window.URL.revokeObjectURL(url)
}

export async function exportFinanceiroCSV() {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/relatorios/financeiro/csv/`, {
    credentials: 'include',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
  })
  if (!response.ok) throw new Error('Erro ao exportar')
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'financeiro.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

export async function getNotificacoes(params?: { tipo?: string; lida?: boolean }) {
  const q = params ? new URLSearchParams(params as any).toString() : ''
  return apiJson(`/api/notificacoes/?${q}`)
}

export async function marcarNotificacaoComoLida(id: string) {
  return apiJson(`/api/notificacoes/${id}/marcar-lida/`, { method: 'POST' })
}

export async function marcarTodasNotificacoesComoLidas() {
  return apiJson('/api/notificacoes/marcar-todas-lidas/', { method: 'POST' })
}
