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

### Exemplo de uso via Python

```python
from descarte.main import cadastrar_coletor, publicar_item, aceitar_match, listar_itens_proximos

# Cadastra um coletor perto de Vitória-ES
cid = cadastrar_coletor(
    lat=-20.3155,
    lng=-40.3128,
    interesses=["madeira", "eletronico"],
    raio_km=5.0
)

# Publica um sofá velho próximo
item_id = publicar_item(
    foto_url="https://exemplo.com/sofa.jpg",
    categoria="madeira",
    lat=-20.3180,
    lng=-40.3100
)

print("Item publicado:", item_id)
print("Itens próximos:", listar_itens_proximos(-20.3155, -40.3128))

# Coletor aceita
aceitar_match(item_id, cid)
```

## Estrutura do projeto

```
descarte/
├── __init__.py
├── models.py          # Item, Coletor, Match
├── store.py           # Armazenamento + expiração
├── proximity.py       # Cálculo de distância e matches
├── notify.py          # Sistema de notificações
├── main.py            # Fluxo principal
└── api.py             # API HTTP (FastAPI)
```

## Status atual

- [x] Lógica de geolocalização (haversine + find_matches)
- [x] Sistema básico de notificações
- [x] Store completo + expiração de itens
- [x] Fluxo de publicação e aceite de match
- [x] API HTTP com FastAPI
- [ ] Testes
- [ ] Persistência real (banco de dados)

## Próximos passos

1. Criar testes simples
2. Persistência com SQLite
3. Evoluir as notificações para push real (Firebase / OneSignal)

## Licença

Projeto em desenvolvimento.
