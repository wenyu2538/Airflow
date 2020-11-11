from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

default_args = {
            'ower': 'wenyu',
            'depends_on_past': False,
            'start_date': days_ago(2),
            'email': ['wwy2538@163.com'],
            'email_on_failure': True,
            'email_on_retry': False,
            'retries': 3,
            'retry_dalay': timedelta(minutes=5),             
            }


dag = DAG(
        'xcom_data',  # 定义的字符串，为dag_id
        default_args=default_args, # 默认参数
        description='a simple tutorial DAG', # 描述
        schedule_interval=timedelta(days=1) # 时间间隔
        )

def t1(**kwargs):
        current_time = datetime.today().strftime("%Y-%m-%d")
        # kwargs['current_time'].xcom_push(key='date',value=current_time)
        return current_time+'www'

def t2(**kwargs):
        print(kwargs)
        ti = kwargs['task_instance']
        print(ti)
        current_tiem = ti.xcom_pull(task_ids='push_task')
        print('*'*10)
        print(current_tiem)
    
push_task = PythonOperator(
        task_id='push_task',
        python_callable=t1,
        provide_context=True,
        dag=dag,
        )

pull_task = PythonOperator(
        task_id='pull_task',
        python_callable=t2,
        provide_context=True,
        dag=dag,
        )

push_task >> pull_task

