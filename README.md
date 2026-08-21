# Tinder do Descarte

Backend + interface web para logística sustentável de resíduos volumosos.

Conecta doadores a cooperativas e artesãos locais com match geográfico, notificações em tempo real, roteirização e métricas de impacto ambiental.

## Interface web

Com a API no ar, abra:

| Página | URL |
|--------|-----|
| Dashboard de impacto | http://localhost:8000/app/ |
| Painel do doador | http://localhost:8000/app/doador.html |
| Painel do coletor | http://localhost:8000/app/coletor.html |
| API docs | http://localhost:8000/docs |

### O que cada painel faz

- **Impacto** — contadores públicos (kg, CO₂, árvores) e últimas coletas
- **Doador** — login, upload de foto (arrastar/soltar), geolocalização e publicação assíncrona
- **Coletor** — login, perfil de raio, WebSocket ao vivo, lista de itens, rota otimizada, aceite e conclusão

## Stack

Python · FastAPI · SQLite · WebSockets · JWT · Docker · HTML/CSS/JS

## Instalação

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

## Fluxo rápido de demo

1. Abra `/app/doador.html` → crie conta doador → publique uma foto com localização
2. Abra `/app/coletor.html` (outra aba) → crie conta coletor → salve o perfil → veja o alerta no WebSocket
3. Aceite o item → otimize a rota → conclua a coleta
4. Volte em `/app/` e veja o impacto atualizado

## Testes

```bash
python -m unittest discover -s tests -v
```

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
- [x] Teste E2E
- [x] Frontend (doador / coletor / impacto)

## Licença

Projeto em desenvolvimento.
