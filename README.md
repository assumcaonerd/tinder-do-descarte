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

## Estrutura inicial do projeto

```
descarte/
├── models.py          # Item, Coletor, Match
├── store.py           # Armazenamento de itens ativos
├── proximity.py       # Cálculo de distância e matches
├── notify.py          # Notificações
└── main.py            # Fluxo principal de publicação e aceite
```

## Próximos passos

1. Implementar modelos e store básico
2. Função de distância geográfica
3. Fluxo de publicação + notificação
4. Expiração automática de itens
5. Aceite de match e atualização de status

## Licença

Projeto em desenvolvimento.
