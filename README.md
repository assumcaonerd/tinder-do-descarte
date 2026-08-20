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

# 2. (Opcional) Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows

# 3. Não há dependências externas no momento
# (as funções de geolocalização usam apenas a biblioteca padrão)
```

### Como testar a lógica de geolocalização

Você pode abrir o Python interativo e importar as funções:

```python
from descarte.proximity import haversine, find_matches
from descarte.models import Item, Coletor
from datetime import datetime, timedelta

# Exemplo rápido de distância
print(haversine(-20.3155, -40.3128, -20.3200, -40.3100))  # ~0.6 km
```

## Estrutura do projeto

```
descarte/
├── __init__.py
├── models.py          # Item, Coletor, Match
├── store.py           # Armazenamento de itens ativos
├── proximity.py       # Cálculo de distância e matches (implementado)
├── notify.py          # Sistema de notificações (implementado)
└── main.py            # Fluxo principal de publicação e aceite
```

## Status atual

- [x] Lógica de geolocalização (haversine + find_matches)
- [x] Sistema básico de notificações
- [ ] Store completo + expiração de itens
- [ ] Fluxo de publicação e aceite de match
- [ ] Interface / API

## Próximos passos

1. Completar o `ItemStore` e a expiração automática
2. Implementar o fluxo em `main.py`
3. Criar testes simples
4. Evoluir as notificações para push real (Firebase / OneSignal)

## Licença

Projeto em desenvolvimento.
