# Tinder do Descarte

Backend para um aplicativo de logística sustentável. Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma a cooperativas de reciclagem e artesãos locais.

O sistema resolve o problema de ponta a ponta: do upload da foto até a confirmação da coleta, passando por notificação em tempo real, otimização de rota e cálculo de impacto ambiental.

## O que o sistema faz

- **Upload com triagem assíncrona** — recebe a foto, responde 202 na hora e processa a IA em background. Só libera o item no mapa se for aprovado.
- **Match geográfico** — Haversine + interesses do coletor.
- **Notificação em tempo real** — WebSocket nativo.
- **Roteirização** — Vizinho Mais Próximo (Nearest Neighbor).
- **Ciclo de vida** — `processando → ativo → aceito → concluido` (ou `rejeitado`).
- **Impacto ambiental** — peso desviado de aterro + CO₂ estimado + equivalência em árvores.

## Stack

- Python 3.10+
- FastAPI + Uvicorn
- SQLite
- WebSockets
- BackgroundTasks (processamento assíncrono)

## Instalação

```bash
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodar

```bash
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

- Docs: http://localhost:8000/docs
- Status: http://localhost:8000/status
- Impacto: http://localhost:8000/impacto/global

## Principais endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/coletores` | Cadastrar coletor |
| POST | `/itens` | Publicar item (URL) |
| POST | `/itens/publicar-com-foto` | Upload + triagem em background (202) |
| POST | `/matches/aceitar` | Aceitar coleta |
| POST | `/coletas/otimizar-rota` | Ordenar paradas |
| POST | `/coletas/concluir` | Concluir + pontos verdes |
| GET | `/coletas/historico` | Histórico |
| GET | `/impacto/global` | Impacto ambiental |
| WS | `/notificacoes/conectar/{id}` | Alertas em tempo real |

## Status

- [x] Geolocalização e matching
- [x] Notificações WebSocket
- [x] Upload + triagem assíncrona (BackgroundTasks)
- [x] Persistência SQLite
- [x] Roteirização
- [x] Histórico + pontos verdes
- [x] Impacto ambiental
- [x] Testes básicos
- [ ] Autenticação (JWT)

## Licença

Projeto em desenvolvimento.
