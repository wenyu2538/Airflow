## 1.快速安装

通过虚拟环境安装：

1.安装airflow

```shell
pip install apache-airflow
```

可能会遇到

![image-20201106131641020](D:\ty文档\Airflow.assets\image-20201106131641020.png)

解决：

从https://www.lfd.uci.edu/~gohlke/pythonlibs/找到对应版本 .whl的安装包。下载到对应环境的Scripts中。如“D:\Anaconda\Scripts>”在当前工作目录下输入指令：pip install 下载的.whl文件。即可

2.设置$AIRFLOW_HOME的环境变量，并初始化数据库

```shell
echo "export AIRFLOW_HOME=~/airflow" >> ~/.bashrc
source ~/.bashrc
#初始化数据库
airflow initdb
```

3. start the web server, default port is 8080

```shell
airflow webserver -p 8080
# -D参数是后台启动
```

4. 在airflow目录下创建dags目录，并编写DAG 的py文件
   1.使用如下代码测试代码正确性：

```shell
python ~/airflow/dags/tutorial.py
```

如果没有抛出异常，证明没有错误，且Airflow环境健全。

​		2.查看所有dag

```shell
airflow list_dags
```

如下图就是当前拥有的dag

![image-20201110135810720](D:\ty文档\Airflow.assets\image-20201110135810720.png)

​		3.查看dag中的Task

```shell
airflow list_tasks xcom_data
```

可以看到xcom_data的dag中有pull_task和push_task两个task

![image-20201110140354414](D:\ty文档\Airflow.assets\image-20201110140354414.png)

​		4.查看任务层次结构

```shell
airflow list_tasks xcom_data --tree
```

可以看到两个Task的层次。

![image-20201110141306554](D:\ty文档\Airflow.assets\image-20201110141306554.png)

​		5.测试Task

```shell
# airflow test DAG_id Task_id date
airflow test xcomdata push_task 20201110
```

task测试结果，图注是返回值。

![image-20201110142540736](D:\ty文档\Airflow.assets\image-20201110142540736.png)

5. 开始调度器
   调度程序将发送任务进行执行。默认Airflow设置依赖于一个名为'SequentialExecutor'的执行器，它由调度程序自动启动。在生产中，可以使用更强大的执行器，如'CeleryExecutor'。

```shell
airflow scheduler
# -D 参数是后台运行
```

访问 localhost:8080查看样例

##  2.基本配置

1.DAG存放目录：
	需要创建~/airflow/dags目录，此目录是默认存放DAG的，想要修改可以更改~/airflow/airflow.cfg文件

2.修改airflow数据库：
	Airflow会使用sqlite作为默认数据库，此情况下，Airflow进行调度任务都只能单个执行。在调度任务量不大的情况下，可以使用sqlite作为backend，如果想要扩展，需要修改配置文件，推荐使用mysql或postgresql。

## 3.参数传递

### 1.PythonOperator参数传递

第一种是Variable.set 和Variable.get。

第二种是使用Xcoms引用上一个task的返回值。

方法1：

在AirflowDAG中，从airflow.models导入Variable。使用Variable.set先设置变量；然后在另外一个Task里面使用Variable.get获取参数。设置变量时可以使用deserialize_json参数，deserializer_json=True时，表示被设置的变量为序列化对象；后面使用Variable.get获取此变量的地方，也需要对应加上deserialize_json参数。

Variable方法查看[Variable源码文档](https://airflow.apache.org/_modules/airflow/models/variable.html#Variable.set)

```python
from airflow.models import Variable

def print_context(ds, **kwargs):
    Variable.set('flag1', 'print_context flag1')    		# Variable.set('flage1', 'print_context flag1', deserialize_json=True)
    print(kwargs)
    print("print_context ds:", ds, len(ds))
    return 'set variable'

run_this = PythonOperator(
	task_id='print_the_context',
    provide_context=True,
    python_callable=print_context,
    dag=dag,
)

def sleep_function(random_base):
    flag1 = Variable.get('flag1')
    # flag1 = Variable.get('flage1', deserialize_json=True)
    print("vatiable_get flag1:",flag1)
    time.sleep(random_base)

for i in range(5):
    task = PythonOperator(
    	task_id='sleep_for_' + str(i)
        python_callable=sleep_function,
        op_kwargs={'random_base': float(i) / 10},
        dag=dag,
    )
    
run_this >> task
```

执行结果：

![image-20201109150205715](D:\ty文档\Airflow.assets\image-20201109150205715.png)

方法2：xcom

在task A中使用return返回要被task B引用的变量；在Task B中直接使用xcom_pull即可引用该变量。

或者可以先数据push进kwargs中

```python
from datetime import datetime
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

dag = DAG(
    dag_id='test_python_variable',
    start_date=datetime.now(),
    default_args=default_args,
    schedule_interval=timedelta(days=1)
)

def push_function(**kwargs):
    ls = ['a', 'b', 'c']
    # 将数据push进kwargs['ti']或kwargs['task_instance']
    kwargs['task_instance'].xcom_push(key='push1', value='lalaa')
    return ls

push_task = PythonOperator(
	task_id='push_task',
    python_callable=push_function,
    provide_context=True,
    dag=dag,
	)

def pull_function(**kwargs):
    print("pull_function kwargs:", kwargs)
    ti = kwargs['ti']
    # kwargs['ti']和kwargs['task_instance']都可以
    ls = ti.xcom_pull(task_ids='push_task')
    push1 = kwargs['task_instance'].xcom_pull(key='push1', task_ids='push_task')
    print(ls)

pull_task = PythonOperator(
	task_id='pull_task',
    python_callable=pull_function,
    provide_context=True,
    dag=dag,
	)
push_task >> pull_task
```

执行结果：

push_task这个Task执行完后Return的值如下所示。

![image-20201109155748854](D:\ty文档\Airflow.assets\image-20201109155748854.png)

push_task这个Task执行完后Xcom的内容如下所示。

![img](http://bigbigben.com/2019/09/20/airflow-python-operator-variable/push_task_xcom.jpg)

pull_task执行过程中打印出了变量ls的值，说明参数传递成功。

![image-20201109155850797](D:\ty文档\Airflow.assets\image-20201109155850797.png)

方法2是从StackOverflow翻出来的，[参考链接](https://stackoverflow.com/questions/46059161/airflow-how-to-pass-xcom-variable-into-python-function)

### 2.传参给DAG

1.使用命令行

2.使用API

1.通过命令行启动DAG时传参

```shell
airflow trigger_dag <dag_id> -c <json格式字符串参数>
# 例
airflow trigger_dag dag_parameter -c '{"id": 1, "start_date": "2020-11-01", "end_date": "2020-11-30"}'
```

获取方式：
	以上方式传参会将参数放在‘kwargs['dag_run'].conf’中。

```python
def get_params(**kwargs):
    id = kwargs.get('dag_run').conf.get('id')
    start_date = kwargs.get('dag_run').conf.get('start_date')
    end_date = kwargs.get('dag_run').conf.get('end_date')
```

