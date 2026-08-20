# Tinder do Descarte

Aplicativo de geolocalização para descarte responsável de resíduos volumosos.

Conecta pessoas que precisam descartar móveis, eletrônicos e materiais de reforma com artesãos, recicladores e pontos de coleta do bairro.

## Ideia central

- O doador tira uma foto do item, escolhe a categoria e publica a localização.
- Coletores e artesãos recebem notificações de itens próximos.
- Sistema de match simples por proximidade + interesses.
- Itens expiram automaticamente se ninguém coletar (mantém o mapa limpo).
- Validação automática da foto por IA simulada (rejeita lixo doméstico).

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

### Endpoint de upload com validação de IA

```
POST /itens/publicar-com-foto
```

Envia:
- `latitude` (form)
- `longitude` (form)
- `file` (imagem JPG/PNG)
- `validade_horas` (opcional, padrão 48)

A IA simulada:
- Rejeita imagens que parecem lixo doméstico/orgânico
- Detecta automaticamente a categoria (madeira, eletronico, metal, outros)
- Salva a foto em `/static/uploads/` e retorna a URL pública

### Rodar os testes

```bash
python -m unittest discover -s tests -v
```

O banco SQLite (`tinder_descarte.db`) é criado automaticamente na primeira execução.

## Estrutura do projeto

```
descarte/
├── __init__.py
├── models.py
├── store.py
├── db.py
├── proximity.py
├── notify.py
├── main.py
└── api.py

static/uploads/     # Fotos enviadas pelos usuários
tests/
```

## Status atual

- [x] Lógica de geolocalização
- [x] Sistema de notificações
- [x] Store + expiração
- [x] Fluxo de publicação e aceite
- [x] API HTTP com FastAPI
- [x] Testes básicos
- [x] Persistência SQLite
- [x] Upload de foto + validação simulada de IA

## Próximos passos possíveis

- Autenticação de usuários
- Modelo real de visão computacional
- Push notifications (Firebase / OneSignal)
- Roteirização inteligente de coletas
- Painel administrativo

## Licença

Projeto em desenvolvimento.
