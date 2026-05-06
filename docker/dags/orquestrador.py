from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from src.extract_and_load import main_extract

with DAG(

    dag_id='coin_gecko',
    start_date=datetime(2024,1,1),
    schedule="*/5 * * * *",
    catchup=False

    ) as dag:

    extract_load_bq = PythonOperator(
        task_id='extract_load_bq',
        python_callable=main_extract
        )