# UpSuporte

Sistema de ordens de servico para equipes de suporte tecnico, com fluxo de gestao, manutencao e historico, projetado para operacao interna.

## Visao geral

- Dashboard com filtros e busca por OS, aparelho e cliente
- Atribuicao de tecnico e notificacao por email
- Aceite/rejeicao de OS pelo tecnico
- Registro de manutencao com fotos (ate 3 imagens)
- SLA por prioridade com alerta de atraso
- Historico de mudancas e comentarios internos

## Requisitos

- Python 3.11+ (recomendado)
- Django 4.2+
- Pillow (upload de imagens)
- PostgreSQL (para producao) ou SQLite (dev local)

## Setup local

1) Criar ambiente virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install Pillow
```

2) Configurar variaveis de ambiente
Crie `.env` na raiz do projeto:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
DEFAULT_FROM_EMAIL=seu_email@gmail.com

SITE_URL=http://127.0.0.1:8000

DATABASE_URL=postgresql://USER:PASS@HOST:PORT/DB

SLA_HORAS_BAIXA=72
SLA_HORAS_MEDIA=48
SLA_HORAS_ALTA=24
```

3) Migracoes e execucao
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Banco de dados

- Em dev, se `DATABASE_URL` nao estiver definido, o projeto usa SQLite.
- Em producao, use PostgreSQL com `DATABASE_URL`.

## Emails de notificacao

As notificacoes sao enviadas para o email do tecnico quando uma OS e atribuida.
Para Gmail, use senha de app.

## Media (fotos)

As fotos de manutencao sao salvas em `media/`.
Em producao, configure storage adequado (S3, R2, etc).

## Deploy (exemplo Railway/Render)

1) Defina variaveis de ambiente no painel do provedor:
`DATABASE_URL`, `EMAIL_*`, `SITE_URL`, `SLA_HORAS_*`
2) Rode migracoes no ambiente.
3) Garanta storage para `media/` (ou use storage externo).

## Comandos uteis

```bash
python manage.py createsuperuser
python manage.py check
```

## Licenca

Projeto interno. Ajuste conforme sua politica.
