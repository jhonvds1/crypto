import requests
import json
import logging
import os
from datetime import datetime, timezone
from google.cloud import bigquery

# URL base da API da CoinGecko
BASE = "https://api.coingecko.com/api/v3"

# Configuração do logger para rastrear execução do pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger_extract = logging.getLogger("EXTRACT")


def load_bq(data: dict | list, filename: str) -> None:
    """
    Carrega dados (dict ou list) para o BigQuery.
    Adiciona timestamp de ingestão e faz load direto na tabela.
    """

    # Marca o momento da ingestão dos dados
    ingestion_date = datetime.now(timezone.utc).isoformat()

    # Dataset onde os dados serão armazenados
    dataset_id = "coingecko-494900.bronze"

    dataset = bigquery.Dataset(dataset_id)

    # Região do dataset no BigQuery
    dataset.location = "US"

    # Nome completo da tabela destino
    table_id = f"coingecko-494900.bronze.{filename}"

    logger_extract.info("Iniciando carga de : %s", table_id)

    # Cliente do BigQuery
    client = bigquery.Client()

    # Cria dataset caso não exista
    client.create_dataset(dataset, exists_ok=True)

    # Configuração do job de load
    job_config = bigquery.LoadJobConfig(
        autodetect=True,              # BigQuery tenta inferir schema automaticamente
        write_disposition="WRITE_TRUNCATE"  # sobrescreve tabela a cada execução
    )

    # Adiciona coluna de ingestão em cada registro
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item['ingested_at'] = ingestion_date

    elif isinstance(data, dict):
        data['ingested_at'] = ingestion_date

    # Envia dados para o BigQuery
    if isinstance(data, list):
        job = client.load_table_from_json(data, table_id, job_config=job_config)
    else:
        job = client.load_table_from_json([data], table_id, job_config=job_config)

    # Aguarda conclusão do job
    job.result()

    logger_extract.info("Tabela salva: %s", table_id)

def last_30_days(moeda: str):
    dias = 30
    moeda_fiat = "usd"
    url = (
        f"https://api.coingecko.com/api/v3/coins/"
        f"{moeda}/market_chart"
        f"?vs_currency={moeda_fiat}&days={dias}"
    )   

    response = requests.get(url)

    data = response.json()

    history = []

    days_gone = set()

    for timestamp, price in data["prices"]:
        data_obj = datetime.fromtimestamp(timestamp / 1000)
        day = data_obj.strftime("%d-%m-%Y")

        if day not in days_gone:
            days_gone.add(day)

            history.append({
                "data": day,
                "preco_usd": round(price, 2)
            })

def extract_crypto_list(base: str) -> None:
    """Extrai lista de todas as criptomoedas disponíveis na CoinGecko."""

    url = f"{base}/coins/list"
    logger_extract.info("Iniciando extração: crypto_list | url=%s", url)

    try:
        # Requisição para API
        response = requests.get(url)

        # Converte resposta em JSON
        data = response.json()

        # Verifica se requisição foi bem sucedida
        response.raise_for_status()

        data = response.json()

        # Carrega dados no BigQuery
        load_bq(data, "crypto_list")

        logger_extract.info("Extração concluída: crypto_list (%d itens)", len(data))

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_crypto_list: %s", e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_crypto_list")

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_crypto_list")

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_crypto_list: %s", e)


def extract_current_market(base: str) -> None:
    """
    Extrai mercado atual das top 100 criptomoedas por market cap.
    """

    url = f"{base}/coins/markets"

    # Parâmetros da requisição
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1
    }

    logger_extract.info("Iniciando extração: current_market | url=%s", url)

    try:
        response = requests.get(url, params=params)

        # Valida status HTTP
        response.raise_for_status()

        # Converte resposta
        data = response.json()

        # Envia para BigQuery
        load_bq(data, "current_market")

        logger_extract.info("Extração concluída: current_market (%d itens)", len(data))

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_current_market: %s", e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_current_market")

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_current_market")

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_current_market: %s", e)


def extract_price_history(base: str, coin_id: str) -> None:
    """
    Extrai histórico de preços dos últimos 30 dias de uma criptomoeda.
    """

    url = f"{base}/coins/{coin_id}/market_chart"

    params = {
        "vs_currency": "usd",
        "days": 30
    }

    logger_extract.info("Iniciando extração: price_history | coin=%s | url=%s", coin_id, url)

    try:
        response = requests.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        # Nome da tabela inclui coin_id
        load_bq(data, f"price_history_{coin_id}")

        logger_extract.info("Extração concluída: price_history | coin=%s", coin_id)

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_price_history (%s): %s", coin_id, e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_price_history (%s)", coin_id)

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_price_history (%s)", coin_id)

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_price_history (%s): %s", coin_id, e)


def extract_overview(base: str) -> None:
    """Extrai dados globais do mercado de criptomoedas."""

    url = f"{base}/global"

    logger_extract.info("Iniciando extração: overview | url=%s", url)

    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        load_bq(data, "overview")

        logger_extract.info("Extração concluída: overview")

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_overview: %s", e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_overview")

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_overview")

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_overview: %s", e)


def extract_trending(base: str) -> None:
    """Extrai criptomoedas em tendência nas últimas 24h."""

    url = f"{base}/search/trending"

    logger_extract.info("Iniciando extração: trending | url=%s", url)

    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        load_bq(data, "trending")

        logger_extract.info("Extração concluída: trending")

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_trending: %s", e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_trending")

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_trending")

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_trending: %s", e)


def extract_coin_details(base: str, coin_id: str) -> None:
    """
    Extrai detalhes completos de uma criptomoeda.
    """

    url = f"{base}/coins/{coin_id}"

    logger_extract.info("Iniciando extração: coin_details | coin=%s | url=%s", coin_id, url)

    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        load_bq(data, f"coin_details_{coin_id}")

        logger_extract.info("Extração concluída: coin_details | coin=%s", coin_id)

        logger_extract.info("Selecionando campos: coin_details | coin=%s", coin_id)

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_coin_details (%s): %s", coin_id, e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_coin_details (%s)", coin_id)

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_coin_details (%s)", coin_id)

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_coin_details (%s): %s", coin_id, e)


def extract_simple_price(base: str) -> None:
    """Extrai preço atual de Bitcoin e Ethereum."""

    url = f"{base}/simple/price"

    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }

    logger_extract.info("Iniciando extração: simple_price | url=%s", url)

    try:
        response = requests.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        load_bq(data, "simple_price")

        logger_extract.info("Extração concluída: simple_price")

    except requests.exceptions.HTTPError as e:
        logger_extract.error("Erro HTTP em extract_simple_price: %s", e)

    except requests.exceptions.ConnectionError:
        logger_extract.error("Falha de conexão em extract_simple_price")

    except requests.exceptions.Timeout:
        logger_extract.error("Timeout em extract_simple_price")

    except Exception as e:
        logger_extract.exception("Erro inesperado em extract_simple_price: %s", e)


def main_extract():
    """Executa pipeline de extração."""

    base = BASE

    logger_extract.info("Extração iniciada")

    extract_current_market(base)
    extract_trending(base)

    logger_extract.info("Extração finalizada com sucesso")


if __name__ == "__main__":
    main_extract()