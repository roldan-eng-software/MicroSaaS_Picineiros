Plano de Continuidade do Projeto MicroSaaS “Picineiros”
Abaixo segue uma análise técnica do estado atual do projeto (backend e frontend), lacunas identificadas, riscos, e um plano de execução em fases para evoluir de um MVP sólido para um produto MicroSaaS pronto para produção, com foco em segurança, escalabilidade, UX, monetização e operação.

1) Entendimento do Estado Atual
1.1 Backend (Django 6 + DRF + Celery + Redis)
Apps principais:
accounts: Usuário customizado (UUID, email como username), autenticação via JWT (SimpleJWT), login/refresh com CSRF e refresh_token via cookie (httponly).
clientes: CRUD com soft-delete (campo ativo). Filtro por ativo e tipo_piscina.
agendamentos: CRUD com soft-delete, status (pendente/confirmado/cancelado/realizado), gatilho de notificação ao criar.
financeiro: Lançamentos vinculados a cliente e opcionalmente a agendamento, status (pendente/pago), ordenação por vencimento.
notificacoes: Modelo e tasks (Celery) para agendamento criado, lembretes de agendamento (D-1), vencimentos e vencidos (até 3 dias).
dashboard: endpoint agregando totais, receita mensal (últimos 6 meses), próximos agendamentos e somatórios por status.
relatorios: export CSV/PDF para clientes, agendamentos e financeiro (usa reportlab).
Infra:
Config Celery com Redis local.
CORS/CSRF limitados a env FRONTEND_ORIGIN.
Rate limit para login (“5/15m”). Permissões padrão IsAuthenticated globalmente.
Banco:
Padrão para dev: SQLite. Suporte configurável via env (DB_ENGINE etc.).
Índices essenciais adicionados (bom para escalabilidade).
Segurança:
Refresh token em cookie HttpOnly com samesite Lax (secure = !DEBUG).
Acesso JWT no header. CSRF aplicado em endpoints sensíveis (login/refresh/logout).
Observações positivas:
Separação clara por domínio.
Soft delete consistente em entidades core.
Notificações assíncronas (bom para UX).
Dashboard com estatísticas úteis.
1.2 Frontend (React + Vite + TS)
Páginas:
Login, Dashboard, Clientes, ClienteEdit, Agendamentos, AgendamentoEdit, Financeiro, FinanceiroEdit, Notificações.
Auth:
Contexto de autenticação, API de login/refresh, hook de inatividade (logout automático).
Rotas:
Organizacao por pages, rotas definidas em src/routes.tsx.
Observações:
Estrutura pronta para consumir APIs atuais.
Provável uso de fetch/axios via src/auth/api.ts com inclusão de token.
2) Lacunas e Pontos de Atenção
Autenticação/contas:
Não há fluxo de cadastro/convite/recuperação de senha no backend exposto via API.
Ausência de verificação de e-mail e redefinição de senha (Django Password Reset).
Multi-tenant / Escopo de dados:
Hoje o “tenant” é o próprio usuário. Para escalar para times/equipes, faltariam entidades “Organização/Plano” e associação do usuário.
Sem ocultação explícita de dados de outros usuários (há filtros por request.user em queries — bom), mas falta validação de ownership nos endpoints de listagem quando filtrados via querystring (já filtra pelo usuário; OK).
Observabilidade:
Log básico apenas em accounts. Falta padronização de logs em todos os apps e configuração para produção (estruturação, Sentry).
Tasks/Agendamentos (Celery Beat):
Há uso de django_celery_beat, mas falta configuração/cron para rodar lembretes e notificações de vencimento em produção.
Pagamentos/Monetização:
Não há integração com gateway (Assinaturas recorrentes, trial, cobrança).
Exportação/Relatórios:
Uso de reportlab direto com estilos simples; suficiente, mas sem paginação/cabecalho detalhado/logotipo.
i18n/Localização:
LANGUAGE_CODE = en-us; Timezone Celery = America/Sao_Paulo. Padronizar idioma/locale do Django (pt-br) e formatos.
Segurança/CORS:
CORS/CSRF dependem de FRONTEND_ORIGIN único. Para ambientes multi (staging/prod), usar lista ou padrão curinga controlado.
Migração de DB:
Produção deve usar Postgres. SQL específicos em dashboard usam “strftime” (SQLite). Isso quebra em Postgres. Necessário reescrever agregação mensal com funções compatíveis.
Testes:
Estrutura de tests.py nos apps, mas sem conteúdo. Falta cobertura de testes unitários e de integração (auth, CRUD, permissões, tasks).
Deploy:
Não há docker-compose ou instruções de deploy (gunicorn, nginx, worker, beat).
Rate limiting:
Só aplicado em login. Considerar limites em listagens e ações intensivas.
3) Perguntas Abertas e Assunções
Modelo de negócio:
Assunção: MicroSaaS com assinatura mensal para profissionais autônomos (1 usuário por conta inicialmente). Confirmar necessidade de equipes/membros.
Requisitos de pagamento:
Preferência por Mercado Pago, Stripe, Pagar.me, Asaas? Precisa de boletos/PIX/Cartão?
Notificações externas:
Atual interesse em e-mail/WhatsApp/SMS? Atualmente só notificação interna via DB.
Regras de negócio financeiras:
Precisamos de conciliação/pagamentos registrados no app? Campos adicionais (multa, desconto, anexo de comprovante)?
Escopo do dashboard e relatórios:
Precisam de filtros por período/cliente/status? Exportações por intervalo?
4) Riscos Técnicos
Incompatibilidade de consultas de receita mensal no Postgres (uso de SQLite strftime).
Tarefas periódicas sem agendamento efetivo em produção.
Segurança de cookies/CSRF/CORS se FRONTEND_ORIGIN não estiver alinhado aos domínios de deploy.
Falta de testes automatizados pode introduzir regressões.
Múltiplas zonas de tempo e formatação de datas/valores no frontend/back.
5) Plano de Execução por Fases
Fase 1 — Endurecimento para Produção (Infra, Segurança, DB)
Banco de dados
Migrar para Postgres (ENV: DB_ENGINE=django.db.backends.postgresql).
Ajustar query de “receita_mensal” para Postgres:
Usar TruncMonth/annotate:
from django.db.models.functions import TruncMonth
receita_mensal = (
  Financeiro.objects.filter(usuario=user, ativo=True, status="pago", criado_em__gte=seis_meses_atras)
  .annotate(month=TruncMonth("criado_em"))
  .values("month")
  .annotate(total=Sum("valor"))
  .order_by("month")
)

Copy

Insert

Configurações de produção
DEBUG=false, SECRET_KEY via ENV, ALLOWED_HOSTS setados.
CORS_ALLOWED_ORIGINS como lista (vários domínios).
Cookies: garantir Secure/HttpOnly/SameSite em produção.
LOGGING: configurar logs estruturados (JSON) e Sentry (opcional).
Celery e Beat
Configurar docker-compose com:
web (gunicorn), worker (celery worker), beat (celery beat), redis, postgres.
Registrar jobs no django_celery_beat:
criar_notificacao_lembrete_agendamento: diário 06:00.
criar_notificacoes_vencimento: diário 07:00.
Testes e QA
Adicionar testes unitários para:
Auth: login/refresh/logout fluxo e CSRF.
CRUD clientes/agendamentos/financeiro com ownership.
Soft-delete comportamento.
Tasks gerando notificações.
Dashboard (com Postgres functions).
Configurar GitHub Actions (pytest, isort/black/ruff, mypy opcional).
Critérios de sucesso:

Deploy local com docker-compose subindo tudo e testes passando.
Endpoints funcionando com Postgres.
Jobs rodando e gerando notificações.
Fase 2 — UX/Funcionalidades Essenciais
Contas/Usuários
Endpoints para:
Registro (opcionalmente com convite).
Alteração de senha e reset via e-mail (Django PasswordResetTokenGenerator).
Verificação de e-mail (token por e-mail).
Notificações externas (opcional nesta fase)
Integrar envio de e-mail para lembretes e vencimentos (SMTP/Sendgrid).
Frontend UX
Filtros por período em dashboard e relatórios.
Máscaras e validações (CPF/telefone).
Internacionalização (pt-BR), datas/valores formatados.
Relatórios
Filtros por período.
Cabeçalho com logo/nome do usuário no PDF.
Critérios de sucesso:

Usuário consegue se registrar, confirmar e recuperar senha.
Dashboard e relatórios com filtros básicos por data.
E-mails de lembrete/vencimento funcionando (se habilitado).
Fase 3 — Monetização e Planos (MicroSaaS)
Modelagem
Modelos: Plano, Assinatura, Faturas.
Atributos: limite de clientes/agendamentos/notificações, trial, preço mensal.
Chaves:
User -> Assinatura (ativa) ou Organização -> Membros (futuro).
Integração de pagamentos
Escolher gateway (Stripe para cartão global, Mercado Pago/Asaas para BR com boleto/PIX).
Fluxos:
Trial 7/14 dias.
Assinatura e cobrança recorrente.
Webhooks para status (paid, past_due, canceled).
Enforcement
Checagem de limites no backend (signals/validators) e feedback no frontend.
Critérios de sucesso:

Usuário assina plano, possui trial, e sistema aplica limites.
Webhooks atualizam status de assinatura.
Bloqueio/advertência ao exceder limites.
Fase 4 — Observabilidade e Operação
Telemetria
Sentry para backend e frontend.
Métricas com Prometheus/Grafana (opcional).
Auditoria
Logs de ações-chave (criação/alteração/exclusão).
Histórico de login/logout.
Backups e retenção
Backup de Postgres e estratégia de retenção.
Políticas de LGPD (se aplicável).
Critérios de sucesso:

Incidentes rastreáveis.
Backups testados e restauráveis.
6) Mudanças de Código Prioritárias (Resumo)
Ajustar “receita_mensal” para Postgres com TruncMonth.
Adicionar endpoints de registro/reset e integração e-mail.
Agendamentos Celery Beat via django_celery_beat.
Testes automatizados abrangentes (auth, CRUD, tasks, dashboards).
Docker-compose para up de todo stack.
Exemplo de docker-compose (ilustrativo):

version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: piscines
      POSTGRES_USER: piscines
      POSTGRES_PASSWORD: changeme
    ports: ["5432:5432"]
    volumes: [dbdata:/var/lib/postgresql/data]

  redis:
    image: redis:7
    ports: ["6379:6379"]

  web:
    build: ./backend
    command: gunicorn config.wsgi:application -b 0.0.0.0:8000
    environment:
      DJANGO_DEBUG: "false"
      DB_ENGINE: django.db.backends.postgresql
      DB_NAME: piscines
      DB_USER: piscines
      DB_PASSWORD: changeme
      DB_HOST: db
      DB_PORT: "5432"
      FRONTEND_ORIGIN: https://app.example.com
    depends_on: [db, redis]
    ports: ["8000:8000"]

  worker:
    build: ./backend
    command: celery -A config worker -l info
    environment: [same as web]
    depends_on: [db, redis, web]

  beat:
    build: ./backend
    command: celery -A config beat -l info
    environment: [same as web]
    depends_on: [db, redis, web]

volumes:
  dbdata:

Copy

Insert

7) Itens Específicos a Investigar/Confirmar
Necessidade de multiusuário por conta (Organização/Equipe).
Gateway de pagamentos preferido e métodos aceitos (PIX, boleto, cartão).
Política de notificações (apenas internas ou por e-mail/WhatsApp).
Requisitos de LGPD/termos/privacidade.
Necessidade de upload de anexos (comprovantes, fotos de serviço).
Escalonamento de agendamentos em calendário (integração Google Calendar?).
8) Critérios de Aceite Gerais
API estável, testada em Postgres, com documentação mínima (OpenAPI/DRF schema).
Deploy automatizado (dev/staging/prod) com CI/CD e testes.
Observabilidade mínima (Sentry) e logs padronizados.
Monetização ativa ou pronta para ativação (sandbox a produção).
UX consistente com validações e mensagens claras.
9) Próximos Passos Imediatos (1–2 Sprints)
Sprint 1:

Ajustar receita_mensal para Postgres.
Adicionar docker-compose e arquivos de deploy.
Configurar Celery Beat com tarefas diárias e criar entradas no django_celery_beat.
Cadastrar testes para auth, CRUD e tasks.
Revisar CORS/CSRF e cookies nos ambientes.
Sprint 2:

Implementar registro/confirmar e reset de senha via e-mail.
Filtros por data no dashboard e relatórios.
i18n pt-BR no backend e formatação no frontend.
Sentry backend/frontend.
Definir gateway de pagamentos e iniciar PoC de assinatura.
Este plano orienta a evolução do MVP para um MicroSaaS pronto para produção com base no código existente. Caso necessário, posso detalhar cada tarefa com issues técnicas, estimativas e checklists de execução.