from airflow import DAG
from datetime import datetime
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

with DAG(
    dag_id='coin_gecko',
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False
) as dag:

    extract_load_bq = DockerOperator(
        task_id='extract_load_bq',
        image='extract_and_load:1.5',
        api_version="auto",
        auto_remove="success",
        command="python3 extract_and_load.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",

        mounts=[
            Mount(
                source="/home/jhon/Documentos/bigquery_key.json",
                target="/opt/bigquery_key.json",
                type="bind"
            )
        ],

        environment={
            "GOOGLE_APPLICATION_CREDENTIALS": "/opt/bigquery_key.json"
        },

        mount_tmp_dir=False
    )