# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item e publica a localização.
- Coletores recebem notificações em tempo real via WebSocket.
- Sistema de match por proximidade + interesses.
- Validação automática da foto por IA simulada.
- Roteirização inteligente das coletas.
- Histórico de coletas + pontos verdes (Moedas Verdes).
- Cálculo de impacto ambiental (peso desviado de aterro + CO₂ poupado).

## Ciclo de vida do item

```
disponivel → aceito → concluido
```

Quando a coleta é concluída, o item some do mapa, gera pontos verdes e alimenta as métricas de impacto.

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
- Impacto global: http://localhost:8000/impacto/global

## Principais endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/coletores` | Cadastrar coletor |
| POST | `/itens` | Publicar item |
| POST | `/itens/publicar-com-foto` | Publicar com upload + IA |
| POST | `/matches/aceitar` | Aceitar coleta |
| POST | `/coletas/otimizar-rota` | Otimizar ordem das paradas |
| POST | `/coletas/concluir` | Concluir coleta + gerar pontos |
| GET | `/coletas/historico` | Listar coletas concluídas |
| GET | `/coletas/pontos/{id}` | Total de Moedas Verdes |
| GET | `/impacto/global` | Painel de impacto ambiental |
| GET | `/impacto/coletor/{id}` | Impacto de um coletor |
| WS | `/notificacoes/conectar/{id}` | Alertas em tempo real |

## Status atual

- [x] Geolocalização e matching
- [x] Notificações WebSocket
- [x] Upload de foto + IA
- [x] Persistência SQLite
- [x] Roteirização inteligente
- [x] Histórico de coletas + pontos verdes
- [x] Cálculo de impacto ambiental (CO₂ e peso)
- [x] Testes básicos

## Próximos passos possíveis

- Autenticação de usuários (JWT)
- Push nativo (Firebase)
- Painel administrativo
- Modelo real de visão computacional

## Licença

Projeto em desenvolvimento.
