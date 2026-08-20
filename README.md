# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item e publica a localização.
- Coletores recebem notificações em tempo real via WebSocket.
- Sistema de match por proximidade + interesses.
- Validação automática da foto por IA simulada.
- Roteirização inteligente das coletas (algoritmo do Vizinho Mais Próximo).

## Objetivo

Facilitar a economia circular local, reduzir descarte irregular e gerar matéria-prima para quem trabalha com reciclagem e upcycling.

## Instalação

```bash
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rodar a API

```bash
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

- Documentação: http://localhost:8000/docs
- Status: http://localhost:8000/status
- WebSocket: `ws://localhost:8000/notificacoes/conectar/{coletor_id}`

## Principais endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/coletores` | Cadastrar coletor |
| POST | `/itens` | Publicar item (com URL) |
| POST | `/itens/publicar-com-foto` | Publicar com upload + IA |
| POST | `/matches/aceitar` | Aceitar coleta |
| GET | `/itens/proximos` | Listar itens próximos |
| POST | `/coletas/otimizar-rota` | Otimizar ordem das paradas |
| WS | `/notificacoes/conectar/{id}` | Alertas em tempo real |

## Status atual

- [x] Geolocalização e matching
- [x] Notificações WebSocket em tempo real
- [x] Upload de foto + validação de IA
- [x] Persistência SQLite
- [x] Roteirização inteligente de coletas
- [x] Testes básicos

## Próximos passos possíveis

- Autenticação de usuários
- Histórico de coletas concluídas
- Modelo real de visão computacional
- Push nativo (Firebase) como fallback
- Painel administrativo

## Licença

Projeto em desenvolvimento.
