# 🚀 CoinGecko Data Pipeline (Airflow + Docker + dbt + BigQuery)

## 📊 Visão geral do projeto

Este projeto implementa um **pipeline completo de engenharia de dados** utilizando dados da API da CoinGecko.

Ele cobre todas as etapas de um fluxo moderno de dados:

- 🔄 Extração de dados via API (CoinGecko)
- 🐳 Containerização com Docker
- ☁️ Armazenamento e ingestão no BigQuery
- ⚙️ Orquestração com Apache Airflow
- 🧱 Transformação de dados com dbt (Data Build Tool)
- 📊 Camadas analíticas (staging, dimensões e fato)

---

## 🧠 Objetivo do projeto

O objetivo é simular um **pipeline real de dados em ambiente de empresa**, aplicando conceitos de:

- Engenharia de Dados moderna (ELT)
- Data Warehouse (modelo estrela)
- Automação de pipelines
- Orquestração de workflows
- Transformação analítica com dbt

---

## 🏗️ Arquitetura

```
CoinGecko API
      ↓
Python ELT (Docker)
      ↓
BigQuery (Raw / Bronze Layer)
      ↓
dbt Transformations
      ↓
Staging Layer
      ↓
Dimensional Models (dim_time, dim_crypto)
      ↓
Fact Table (current_market)
      ↓
Dashboard (Power BI / Tableau - em definição)
```

## ⚙️ Tecnologias utilizadas  
Python 3.11  
Apache Airflow  
Docker  
Docker Compose  
dbt (BigQuery adapter)  
Google BigQuery  
CoinGecko API  
SQL (BigQuery Standard SQL)  

```
crypto/
│
│
├── src/
│   └── extract_and_load.py
│
├── dbt_bigquery/
│   └── models/
│       ├── staging/
│       ├── marts/
│       ├── dim_time.sql
│       ├── dim_crypto.sql
│       └── fact_current_market.sql
│
├── docker/
|   ├──config/
│   ├── Dockerfile (Extract e Load)
│   ├── Dockerfile_airflow (DBT)
|   └── dags/
|       └── orquestrador.py (DAG do airflow)
│
├── credentials/
│   └── bigquery_key.json
│
├── diagrama.png
├── requirements.txt
├── .gitignore
└── README.md

```

## 🔄 Como o pipeline funciona  
### 1. Extração de dados (ETL Python)  
Consome API da CoinGecko  
Extrai market data, trending e histórico  
Adiciona timestamp de ingestão  
Envia para o BigQuery (raw layer)  

### 2. Orquestração com Airflow  
### Task 1: extract_load_bq  
Executa container Python  
Extrai dados da API  
Carrega no BigQuery  
### Task 2: dbt_run  
Executa transformações dbt  
Cria staging, dimensões e fatos  

extract_load_bq → dbt_run

### 3. Transformação com dbt  
#### 📌 Staging  
limpeza  
padronização  
deduplicação  
#### 📌 Dimensões  
dim_time  
dim_crypto  
#### 📌 Fact  
fact_current_market  
métricas financeiras e de mercado  

## 🐳 Como executar o projeto
### 1. Clonar repositório

git clone https://github.com/jhonvds1/crypto.git

cd crypto

### 2.  Credenciais BigQuery  
Colocar service account em:

credentials/bigquery_key.json

### 3. Build ETL

docker build -t extract_and_load:1.5 .

### 4. Build dbt
docker build -t dbt_coin:1.2 .

### 5. Subir Airflow
docker-compose up -d

### 6. Acessar UI
http://localhost:8080/

Ativar DAG:
coin_gecko
### 7. Execução


Roda a cada:
*/15 minutos

## 📊 Camadas de dados  
🟤 Bronze: dados brutos da API  
⚪ Silver: staging (limpeza e tratamento)  
🟡 Gold: modelos analíticos (dimensões e fatos)  

## 📈 BI (em desenvolvimento)

Ferramenta a definir:

Power BI
ou Tableau

Possíveis dashboards:

preço de criptos
market cap
trending coins
volume
variação 24h

## 💡 Por que esse projeto importa?

Demonstra habilidades de:  

pipelines end-to-end  
Airflow  
dbt  
SQL analítico  
modelagem estrela  
Docker  
integração com cloud (BigQuery)  

## 🔥 Melhorias futuras  
retries no Airflow  
secrets manager (GCP)  
testes dbt (not_null, unique)  
CI/CD (GitHub Actions)  
data quality checks  
deploy cloud (Composer)  

## 👨‍💻 Autor

Jonatha Viegas da Silva  
Engenharia de Computação - UFPel  
Data Engineer  
GitHub: https://github.com/jhonvds1


## ⭐ Conclusão

Pipeline completo de engenharia de dados do zero até camada analítica pronta para BI.
