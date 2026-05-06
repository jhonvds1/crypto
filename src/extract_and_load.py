import requests
import json
import logging
import os
from datetime import datetime, timezone
from google.cloud import bigquery


BASE = "https://api.coingecko.com/api/v3"

# Pasta onde os JSONs extraídos serão salvos

# Configuração do logger padrão do módulo de extração
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger_extract = logging.getLogger("EXTRACT")


def load_bq(data: dict | list, filename: str) -> None:
    """Salva um dicionário ou lista como arquivo JSON na pasta de saída."""

    ingestion_date = datetime.now(timezone.utc).isoformat()

    dataset_id = "coingecko-494900.bronze"

    dataset = bigquery.Dataset(dataset_id)

    dataset.location = "US"

    table_id = f"coingecko-494900.bronze.{filename}"

    logger_extract.info("Iniciando carga de : %s", table_id)

    client = bigquery.Client()

    client.create_dataset(dataset, exists_ok=True)

    job_config = bigquery.LoadJobConfig(
        autodetect = True,
        write_disposition = "WRITE_TRUNCATE"
    )

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item['ingested_at'] = ingestion_date
    elif isinstance(data, dict):
                data['ingested_at'] = ingestion_date

    if isinstance(data, list):
        job = client.load_table_from_json(data, table_id, job_config=job_config)
    else:
        job = client.load_table_from_json([data], table_id, job_config=job_config)

    job.result()
    logger_extract.info("Tabela salva: %s", table_id)


def extract_crypto_list(base: str) -> None:
    """Extrai a lista completa de criptomoedas disponíveis na CoinGecko."""
    url = f"{base}/coins/list"
    logger_extract.info("Iniciando extração: crypto_list | url=%s", url)
    try:
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()
        data = response.json()
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
    """Extrai os dados de mercado das top 100 criptomoedas por capitalização (em USD)."""
    url = f"{base}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1
    }
    logger_extract.info("Iniciando extração: current_market | url=%s", url)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
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
    Extrai o histórico de preços dos últimos 30 dias de uma moeda específica.

    Args:
        coin_id: identificador da moeda (ex: 'bitcoin', 'ethereum')
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
        # Nome do arquivo inclui o coin_id para evitar sobrescrever dados de outras moedas
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
    """Extrai dados globais do mercado de criptomoedas (capitalização total, dominância, etc.)."""
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
    """Extrai as criptomoedas em tendência (trending) nas últimas 24h."""
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
    Extrai detalhes completos de uma moeda específica (descrição, links, métricas, etc.).

    Args:
        coin_id: identificador da moeda (ex: 'bitcoin', 'ethereum')
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
    """Extrai o preço atual simplificado de Bitcoin e Ethereum em USD."""
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
    """Executa todas as extrações em sequência e salva os resultados em JSON."""
    base = BASE
    logger_extract.info("Extração iniciada")

    extract_current_market(base)
    extract_trending(base)

    logger_extract.info("Extração finalizada com sucesso")


if __name__ == "__main__":
    main_extract()