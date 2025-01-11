import pendulum
from apps import af_utils
from airflow.decorators import dag, task

@dag(
    dag_id=af_utils.get_dag_name(dag_file_path=__file__),
    default_args=af_utils.get_default_args(),
    start_date=pendulum.datetime(year=2025, month=1, day=11),
    schedule=None,
    catchup=False
)
def dag():
    @task
    def print_hello():
        print("Hello world")

    print_hello()


dag()
