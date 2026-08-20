# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item, escolhe a categoria e publica a localização.
- Coletores e artesãos recebem notificações em tempo real via WebSocket.
- Sistema de match por proximidade + interesses.
- Itens expiram automaticamente se ninguém coletar.
- Validação automática da foto por IA simulada (rejeita lixo doméstico).

## Objetivo

Facilitar a economia circular local, reduzir descarte irregular e gerar matéria-prima para quem trabalha com reciclagem e upcycling.

## Instalação

```bash
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
pip install -r requirements.txt
```

## Rodar a API

```bash
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

- Documentação: http://localhost:8000/docs
- Status: http://localhost:8000/status
- WebSocket: `ws://localhost:8000/notificacoes/conectar/{coletor_id}`

## Testar notificação em tempo real

No console do navegador (F12):

```javascript
const ws = new WebSocket("ws://localhost:8000/notificacoes/conectar/marceneiro_vitoria");
ws.onmessage = (event) => console.log("🚨 NOVO ALERTA:", JSON.parse(event.data));
```

Depois publique um item próximo (via `/docs` ou `/itens/publicar-com-foto`). O alerta deve aparecer instantaneamente no console.

## Status atual

- [x] Geolocalização e matching
- [x] Notificações em memória + WebSocket em tempo real
- [x] Store + expiração
- [x] Fluxo de publicação e aceite
- [x] API HTTP com FastAPI
- [x] Upload de foto + validação de IA
- [x] Persistência SQLite
- [x] Testes básicos

## Próximos passos possíveis

- Autenticação de usuários
- Modelo real de visão computacional
- Push nativo (Firebase / OneSignal) como fallback
- Roteirização inteligente de coletas
- Painel administrativo

## Licença

Projeto em desenvolvimento.
