# Análise de Dados — Campanha de Marketing (Meta Ads)

Projeto de tratamento de dados, cálculo de métricas de funil e visualização em Power BI a partir dos relatórios diários de veiculação do Gerenciador de Anúncios da Meta.

## Estrutura do Repositório

```text
.
├── data/
│   ├── raw/
│   │   └── marketing-final-ad.csv
│   └── processed/
│       ├── agg_performance_by_ad.csv
│       ├── data_quality_audit.json
│       ├── fact_daily_active.csv
│       └── powerbi_pronto_por_anuncio.csv
├── powerbi/
│   └── dashboard.pbit
├── src/
│   ├── etl_cleaning.py
│   ├── metrics.py
│   └── run_pipeline.py
├── .gitignore
└── README.md
```

## Contexto e Tratamento da Base (ETL)

A extração bruta (`data/raw/marketing-final-ad.csv`) possui 704 linhas referentes ao cruzamento de 4 anúncios ao longo de 176 dias de calendário (`2026-04-24` a `2026-10-16`). Durante a auditoria e limpeza dos dados via Python (`src/`), foram aplicados os seguintes tratamentos:

1. **Filtragem de dias sem entrega:** Remoção de 681 registros diários zerados gerados pela exportação por calendário, isolando os 23 registros em que houve atividade real de campanha (`24/04/2026` a `15/05/2026`).
2. **Preservação de conversões de janela de atribuição (7d clique / 1d visualização):** Identificação de 4 registros pós-pausa onde o gasto diário foi `R$ 0,00`, mas ocorreram 5 conversas iniciadas atribuídas aos cliques dos dias anteriores. Um filtro simples por `Valor gasto > 0` descartaria 9,26% das conversões reais de mensagem.
3. **Separação de objetivos de campanha:** Segregação entre o conjunto otimizado para tráfego (`actions:link_click`) e o conjunto otimizado para mensagens (`actions:onsite_conversion.messaging_conversation_started_7d`), evitando a soma incorreta de cliques no link com conversas iniciadas.
4. **Limpeza de caracteres e colunas nulas:** Conversão de travessões (`–`, `U+2013`) nas colunas de classificação para valores nulos e descarte de colunas sem variância.
5. **Cálculo ponderado de taxas:** Recálculo de `CPR`, `CPM`, `CPC`, `CTR`, `Hook Rate (3s)` e `Hold Rate (ThruPlay 15s)` a partir das somas consolidadas de cada anúncio, evitando distorções de média simples sobre taxas diárias.

## Principais Resultados da Análise

### 1. Performance Comercial e Conversão

| Anúncio | Objetivo | Período Ativo | Valor Gasto | Impressões | Cliques no Link | CTR Link | Resultados | CPR Ponderado | Conv. Clique -> Resultado |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **video casa da cultura - site** | Tráfego (Link) | 24/04 a 29/04 | R$ 185,56 | 43.003 | 1.543 | 3,59% | 1.543 | R$ 0,12 | 100,00% |
| **Novo anúncio de Engajamento** | Mensagem | 30/04 a 04/05 | R$ 140,81 | 13.661 | 111 | 0,81% | 24 | R$ 5,87 | 21,62% |
| **anuncio porque** | Mensagem | 04/05 a 08/05 | R$ 165,98 | 10.565 | 116 | 1,10% | 23 | R$ 7,22 | 19,83% |
| **anuncio videos naturais 1** | Mensagem | 13/05 a 15/05 | R$ 156,97 | 9.765 | 76 | 0,78% | 7 | R$ 22,42 | 9,21% |

### 2. Funil de Retenção de Vídeo

| Anúncio | Reproduções de Vídeo | Retenção 3s (Hook Rate) | ThruPlay 15s (Hold Rate) | Custo / ThruPlay | Vídeo 25% | Vídeo 50% | Vídeo 75% | Vídeo 100% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **video casa da cultura - site** | 37.834 | 43,34% | 25,63% | R$ 0,039 | 10,7% | 6,5% | 4,7% | 2,6% |
| **Novo anúncio de Engajamento** | 12.320 | 22,90% | 29,51% | R$ 0,153 | 6,2% | 3,5% | 2,5% | 1,3% |
| **anuncio porque** | 9.239 | 27,74% | 27,57% | R$ 0,205 | 9,9% | 5,2% | 3,6% | 2,5% |
| **anuncio videos naturais 1** | 8.875 | 26,35% | 33,31% | R$ 0,183 | 15,2% | 8,4% | 5,8% | 3,3% |

### Destaques Analíticos

- **Aquisição de Tráfego (`video casa da cultura - site`):** Entregou 1.543 cliques no link a R$ 0,12 por clique, com Hook Rate de 43,34% (acima da referência de mercado de 30%) e CTR de link de 3,59%.
- **Eficiência de Conversão em Mensagens (`Novo anúncio de Engajamento` e `anuncio porque`):** Obtiveram taxas de conversão pós-clique de 21,62% e 19,83% (1 conversa iniciada a cada 5 cliques no link), fechando com CPR de R$ 5,87 e R$ 7,22.
- **Retenção de Vídeo vs. Chamada para Ação (`anuncio videos naturais 1`):** Registrou a maior retenção contínua da conta (Hold Rate de 33,31% e 3,3% de retenção até 100% do vídeo), além de reduzir seu CPR diário em 39,9% entre o segundo e o terceiro dia de veiculação (de R$ 17,28 em `14/05` para R$ 10,39 em `15/05`).

## Como Executar

1. Para reprocessar a base bruta e gerar os arquivos tratados em `data/processed/`:

```bash
python -B src/run_pipeline.py
```

2. Para visualizar o painel interativo, abra o arquivo `powerbi/dashboard.pbit` no Microsoft Power BI Desktop.
