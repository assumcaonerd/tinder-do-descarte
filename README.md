# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item e publica a localização.
- Coletores recebem notificações em tempo real via WebSocket.
- Sistema de match por proximidade + interesses.
- Validação automática da foto por IA simulada.
- Roteirização inteligente das coletas.
- Histórico imutável de coletas concluídas + pontos verdes (Moedas Verdes).

## Ciclo de vida do item

```
disponivel → aceito → concluido
```

Quando a coleta é concluída, o item some do mapa e gera pontos verdes para o coletor.

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
| WS | `/notificacoes/conectar/{id}` | Alertas em tempo real |

## Status atual

- [x] Geolocalização e matching
- [x] Notificações WebSocket
- [x] Upload de foto + IA
- [x] Persistência SQLite
- [x] Roteirização inteligente
- [x] Histórico de coletas + pontos verdes
- [x] Testes básicos

## Próximos passos possíveis

- Autenticação de usuários (JWT)
- Estimativa de impacto ambiental (CO₂ / peso)
- Push nativo (Firebase)
- Painel administrativo

## Licença

Projeto em desenvolvimento.
