from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable


default_args={
        'ower': 'wenyu',
        'depend_on_past': False,
        'start_date': days_ago(2),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 3,
        'retry_dalay': timedelta(minutes=5),
        }


dag = DAG(
        dag_id='dag_parameter',
        default_args=default_args,
        description='DAG 参数传递 ',
        schedule_interval=timedelta(days=1)
        )


def my_py_command(ds, **kwargs):
    print(kwargs)
    print('*'*10)
    print(kwargs.get('dag_run'))
    print(kwargs.get('dag_run').conf.get('foo'))
    print(kwargs.get('dag_run').conf)
    print('*'*10)
    if kwargs['test_mode']:
        print(" 'foo' was passed in via test={} command : kwargs[params][foo] \
                               = {}".format(kwargs["test_mode"], kwargs["params"]["foo"]))
    print(f"'miff' was passed in via task_params = {kwargs['params']['miff']}")
    return 2

run_this = PythonOperator(
        task_id='run_task',
        provide_context=True,
        python_callable=my_py_command,
        params={"miff": "aff"},
        dag=dag,
        )
