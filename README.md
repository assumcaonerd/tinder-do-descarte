# Tinder do Descarte

Backend para um aplicativo de logística sustentável. Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma a cooperativas de reciclagem e artesãos locais.

O sistema resolve o problema de ponta a ponta: do upload da foto até a confirmação da coleta, passando por notificação em tempo real, otimização de rota e cálculo de impacto ambiental.

## O que o sistema faz

- **Upload com triagem** — recebe a foto, valida extensão, simula análise por visão computacional e rejeita descartes inválidos (ex.: lixo orgânico).
- **Match geográfico** — usa a fórmula de Haversine para encontrar coletores dentro do raio e com interesse na categoria do item.
- **Notificação em tempo real** — WebSocket nativo: o coletor conectado recebe o alerta no instante em que o item é publicado.
- **Roteirização** — algoritmo do Vizinho Mais Próximo (Nearest Neighbor) para ordenar múltiplas paradas e reduzir deslocamento.
- **Ciclo de vida do item** — `disponivel → aceito → concluido`. A conclusão grava histórico, gera pontos verdes e remove o item do mapa público.
- **Impacto ambiental** — a partir do histórico, estima peso desviado de aterro, CO₂ poupado e equivalência aproximada em árvores.

## Stack

- Python 3.10+
- FastAPI + Uvicorn
- SQLite (persistência)
- WebSockets (notificações)
- Upload de arquivos + validação

## Instalação

```bash
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Rodar

```bash
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

- Documentação interativa: http://localhost:8000/docs
- Status: http://localhost:8000/status
- Impacto global: http://localhost:8000/impacto/global

## Principais endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/coletores` | Cadastrar coletor |
| POST | `/itens` | Publicar item (URL de foto) |
| POST | `/itens/publicar-com-foto` | Publicar com upload + triagem |
| POST | `/matches/aceitar` | Aceitar coleta |
| POST | `/coletas/otimizar-rota` | Ordenar paradas (TSP aproximado) |
| POST | `/coletas/concluir` | Concluir coleta e gerar pontos |
| GET | `/coletas/historico` | Histórico de coletas |
| GET | `/coletas/pontos/{id}` | Total de Moedas Verdes |
| GET | `/impacto/global` | Painel de impacto ambiental |
| GET | `/impacto/coletor/{id}` | Impacto de um coletor |
| WS | `/notificacoes/conectar/{id}` | Canal de alertas em tempo real |

## Testar notificação em tempo real

No console do navegador (F12):

```javascript
const ws = new WebSocket("ws://localhost:8000/notificacoes/conectar/seu_coletor_id");
ws.onmessage = (e) => console.log("Alerta:", JSON.parse(e.data));
```

Publique um item próximo e o alerta deve aparecer na hora.

## Estrutura

```
descarte/
├── api.py          # Rotas HTTP + WebSocket
├── main.py         # Fluxo de publicação e aceite
├── models.py       # Item, Coletor, Match
├── db.py           # Persistência SQLite
├── proximity.py    # Haversine + matching
├── notify.py       # Histórico + WebSocket manager
├── routing.py      # Otimização de rotas
├── historico.py    # Conclusão de coletas + pontos
└── impact.py       # Cálculo de CO₂ e peso
```

## Status

- [x] Geolocalização e matching
- [x] Notificações WebSocket
- [x] Upload de foto + triagem
- [x] Persistência SQLite
- [x] Roteirização
- [x] Histórico + pontos verdes
- [x] Impacto ambiental
- [x] Testes básicos
- [ ] Autenticação (JWT)

## Licença

Projeto em desenvolvimento.
