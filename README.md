# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item, escolhe a categoria e publica a localização.
- Coletores e artesãos recebem notificações de itens próximos.
- Sistema de match simples por proximidade + interesses.
- Itens expiram automaticamente se ninguém coletar (mantém o mapa limpo).

## Objetivo

Facilitar a economia circular local, reduzir descarte irregular e gerar matéria-prima para quem trabalha com reciclagem e upcycling.

## Instalação

### Pré-requisitos

- Python 3.10 ou superior

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/assumcaonerd/tinder-do-descarte.git
cd tinder-do-descarte

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

### Rodar a API

```bash
uvicorn descarte.api:app --reload --host 0.0.0.0 --port 8000
```

Depois abra no navegador:
- Documentação interativa: http://localhost:8000/docs
- Status: http://localhost:8000/status

### Rodar os testes

```bash
python -m unittest discover -s tests -v
```

O banco SQLite (`tinder_descarte.db`) é criado automaticamente na primeira execução.

## Estrutura do projeto

```
descarte/
├── __init__.py
├── models.py          # Item, Coletor, Match
├── store.py           # Store em memória (legado)
├── db.py              # Persistência SQLite
├── proximity.py       # Cálculo de distância e matches
├── notify.py          # Sistema de notificações
├── main.py            # Fluxo principal
└── api.py             # API HTTP (FastAPI)

tests/
├── test_proximity.py
├── test_store.py
└── test_main.py
```

## Status atual

- [x] Lógica de geolocalização (haversine + find_matches)
- [x] Sistema básico de notificações
- [x] Store completo + expiração de itens
- [x] Fluxo de publicação e aceite de match
- [x] API HTTP com FastAPI
- [x] Testes básicos
- [x] Persistência real com SQLite

## Próximos passos possíveis

- Autenticação de usuários
- Upload real de fotos
- Push notifications (Firebase / OneSignal)
- Roteirização inteligente de coletas
- Painel administrativo

## Licença

Projeto em desenvolvimento.
