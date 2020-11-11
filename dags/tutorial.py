from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

# #我们要创建一个DAG和一些task，可以选择显示的方式向每个任务的构造函数传递一组参数。
# #定义一个默认字典，以便在创建task是使用。

# 这些参数将会传递给每个操作符
# 您可以在操作符初始化期间针对每个任务重写它们
default_args = {
    'ower': 'wenyu',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['wwy2538@163.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_dalay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2020, 11, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
#更多的基础参数信息参考airflow.models.BaseOperator--https://airflow.apache.org/docs/stable/_api/airflow/models/index.html#airflow.models.BaseOperator

## 实例化一个DAG
#我们需要一个DAG对象将任务嵌套到其中。在这里，传递一个定义的字符串，该字符串dag_id 用作DAG的唯一标识符##
#也传递了刚刚定义的默认参数字典，并且调度时间间隔定义了1天

dag = DAG(
    'tutorial',  # 定义的字符串，为dag_id
    default_args=default_args, # 默认参数
    description='a simple tutorial DAG', # 描述
    schedule_interval=timedelta(days=1) # 时间间隔
)

## Task


t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag
)

t2 = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5',
    retries=3,
    dag=dag,
)

# 我们使用了一些继承于BaseOperator()的特殊参数，如bash_command，和通用参数，如retries，并且重写了restries
# 任务参数优先级
    # 1.明确传递的参数
    # 2.default_args中定义的
    # 3.默认的参数
# 一个task必须包含或继承task_id 和owner两个参数，否则就会引起Airflow异常

## Jinja模板
# Airflow利用了Jinja模板的功能，为使用者提供了内置参数和宏。Airflow还为使用者提供了钩子（hook），来定义他们自己的参数，宏和模板

template_command = """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(da,7) }}"
        echo "{{ params.my_param }}"
    {% endfor %}
"""

t3 = BashOperator(
    task_id='templated',
    depends_on_past=False,
    bash_command=template_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag,
)

## 设置依赖关系
# t2依赖于t1
# t1.set_downstream(t2)
# t2.set_upstream(t1)
# t1 >> t2
# t2 << t1

# # 多个依赖关系
# t1 >> t2 >> t3
# t1.set_downstream([t2, t3])
t1 >> [t2, t3]
# [t2, t3] << t1
