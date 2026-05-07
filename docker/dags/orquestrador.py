# Importa o Airflow e dependências necessárias
from airflow import DAG
from datetime import datetime

# Operator que permite rodar containers Docker dentro do Airflow
from airflow.providers.docker.operators.docker import DockerOperator

# Classe usada para montar volumes entre host e container
from docker.types import Mount


# Definição do DAG (pipeline)
with DAG(
    dag_id='coin_gecko',                 # nome do pipeline no Airflow
    start_date=datetime(2024, 1, 1),     # data inicial de execução
    schedule="*/15 * * * *",             # executa a cada 15 minutos (cron)
    catchup=False                        # não executa histórico atrasado
) as dag:


    # =========================
    # TASK 1: EXTRAÇÃO + LOAD
    # =========================
    extract_load_bq = DockerOperator(

        task_id='extract_load_bq',       # nome da task no Airflow

        image='extract_and_load:1.5',    # imagem Docker do pipeline Python

        api_version="auto",

        auto_remove="success",           # remove container após sucesso

        command="python3 extract_and_load.py",  # comando executado no container

        docker_url="unix://var/run/docker.sock", # conecta no Docker local

        network_mode="bridge",

        # monta arquivo de credencial do GCP dentro do container
        mounts=[
            Mount(
                source="/home/jhon/Documentos/bigquery_key.json",  # arquivo local
                target="/opt/bigquery_key.json",                   # caminho no container
                type="bind"
            )
        ],

        # variável de ambiente usada pelo Google Cloud SDK
        environment={
            "GOOGLE_APPLICATION_CREDENTIALS": "/opt/bigquery_key.json"
        },

        mount_tmp_dir=False
    )


    # =========================
    # TASK 2: DBT RUN
    # =========================
    dbt_run = DockerOperator(

        task_id='dbt_run',               # task de transformação dbt

        image='dbt_coin:1.2',            # imagem com dbt instalado

        command='dbt run',               # executa todos os models

        docker_url='unix://var/run/docker.sock',

        network_mode='bridge',

        auto_remove='success',

        # monta pasta com credenciais do BigQuery
        mounts=[
            Mount(
                source='/home/jhon/eng_dados_estudos/coin/credentials',
                target='/credentials',
                type='bind'
            )
        ],

        mount_tmp_dir=False
    )


    # =========================
    # DEPENDÊNCIA ENTRE TASKS
    # =========================

    # garante ordem de execução:
    # 1. extract_load_bq
    # 2. dbt_run
    extract_load_bq >> dbt_run