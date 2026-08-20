# Tinder do Descarte

Backend para um aplicativo de logística sustentável. Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma a cooperativas de reciclagem e artesãos locais.

## O que o sistema faz

- Upload com triagem assíncrona (HTTP 202 + BackgroundTasks)
- Match geográfico (Haversine)
- Notificações em tempo real (WebSocket)
- Roteirização (Nearest Neighbor)
- Histórico + Moedas Verdes
- Impacto ambiental (CO₂ e peso)
- Autenticação JWT com papéis (doador / coletor)
- Docker com volumes persistentes

## Stack

Python · FastAPI · SQLite · WebSockets · JWT · Docker

## Instalação local

```bash
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

## Autenticação

1. Cadastre um usuário:
```bash
POST /auth/registro
{ "email": "coletor@email.com", "senha": "123456", "role": "coletor", "nome": "Cooperativa Centro" }
```

2. Faça login (form-urlencoded, como OAuth2):
```bash
POST /auth/login
username=coletor@email.com&password=123456
```

3. Use o token nas rotas protegidas:
```
Authorization: Bearer <access_token>
```

### Quem pode o quê

| Rota | Público | Autenticado | Só coletor |
|------|---------|-------------|------------|
| `/impacto/*`, `/coletas/historico`, `/itens/proximos` | ✓ | | |
| `/itens`, `/itens/publicar-com-foto` | | ✓ | |
| `/coletores`, `/matches/aceitar`, `/coletas/otimizar-rota`, `/coletas/concluir` | | | ✓ |

## Principais endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/registro` | Cadastrar usuário |
| POST | `/auth/login` | Login (JWT) |
| GET | `/auth/me` | Dados do usuário logado |
| POST | `/itens/publicar-com-foto` | Upload + triagem (202) |
| POST | `/coletas/otimizar-rota` | Ordenar paradas |
| POST | `/coletas/concluir` | Concluir coleta |
| GET | `/impacto/global` | Impacto ambiental |
| WS | `/notificacoes/conectar/{id}` | Alertas em tempo real |

## Status

- [x] Geolocalização e matching
- [x] Notificações WebSocket
- [x] Upload + triagem assíncrona
- [x] Persistência SQLite
- [x] Roteirização
- [x] Histórico + pontos verdes
- [x] Impacto ambiental
- [x] Docker
- [x] Autenticação JWT + roles
- [ ] Testes E2E

## Licença

Projeto em desenvolvimento.
