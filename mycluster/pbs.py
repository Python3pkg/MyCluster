import math
import os
from string import Template
import subprocess

from .mycluster import get_data
from .mycluster import load_template

def scheduler_type():
    return 'pbs'

def name():
    return 'pbs'

def queues():
    queue_list = []
    try:
        output = subprocess.check_output(['qstat', '-Q'])
        lines = output.splitlines()[2:]
        for queue in lines:
            queue_list.append(queue.split(' ')[0])
    except Exception as e:
        print("ERROR")
        print(e)
        pass
    return queue_list


def accounts():
    return []


def available_tasks(queue_id):
    free_tasks = 0
    max_tasks = 0
    return {'available': free_tasks, 'max tasks': max_tasks}

def tasks_per_node(queue_id):
    return 2

def min_tasks_per_node(queue_id):
    return 1

def node_config(queue_id):
    return {'max thread': 1, 'max memory': "Unknown"}

def create_submit(queue_id,**kwargs):

    queue_name   = queue_id
    num_tasks = 1
    if 'num_tasks' in kwargs:
        num_tasks = kwargs['num_tasks']

    tpn = tasks_per_node(queue_id)
    queue_tpn = tpn
    if 'tasks_per_node' in kwargs:
        tpn = min(tpn,kwargs['tasks_per_node'])

    nc = node_config(queue_id)
    qc = available_tasks(queue_id)

    if qc['max tasks'] > 0:
        num_tasks = min(num_tasks,qc['max tasks'])

    num_threads_per_task = nc['max thread']
    if 'num_threads_per_task' in kwargs:
        num_threads_per_task = kwargs['num_threads_per_task']
    num_threads_per_task = min(num_threads_per_task,int(math.ceil(float(nc['max thread'])/float(tpn))))

    my_name = kwargs.get('my_name', "myclusterjob")
    my_output = kwargs.get('my_output', "myclusterjob.out")
    my_script = kwargs.get('my_script', None)
    if 'mycluster-' in my_script:
        my_script = get_data(my_script)

    user_email = kwargs.get('user_email', None)
    project_name = kwargs.get('project_name', 'default')

    wall_clock = kwargs.get('wall_clock', '12:00:00')
    if ':' not in wall_clock:
        wall_clock = wall_clock + ':00:00'

    num_nodes = int(math.ceil(float(num_tasks)/float(tpn)))

    if num_nodes == 0:
        raise ValueError("Must request 1 or more nodes")

    num_queue_slots = num_nodes*queue_tpn

    if 'shared' in kwargs:
        if kwargs['shared'] and num_nodes == 1: # Assumes fill up rule
            num_queue_slots = num_nodes*max(tpn,min_tasks_per_node(queue_id))

    no_syscribe = kwargs.get('no_syscribe', False)

    record_job = not no_syscribe

    openmpi_args = kwargs.get('openmpi_args', "-bysocket -bind-to-socket")

    qos = kwargs.get('qos', None)

    template = load_template('pbs.jinja')

    script_str = template.render(my_name = my_name,
                                 my_script = my_script,
                                 my_output = my_output,
                                 user_email = user_email,
                                 queue_name = queue_name,
                                 num_queue_slots = num_queue_slots,
                                 num_tasks = num_tasks,
                                 tpn = tpn,
                                 num_threads_per_task = num_threads_per_task,
                                 num_nodes = num_nodes,
                                 project_name =  project_name,
                                 wall_clock = wall_clock,
                                 record_job = record_job,
                                 openmpi_args =  openmpi_args,
                                 qos = qos)

    return script_str


def submit(script_name, immediate, depends=None):
    job_id = None
    with os.popen('qsub' + script_name) as f:
        job_id = 0
        try:
            job_id = f.readline.strip()
        except:
            print('Failed to launch job')
            print(f.readline())
            pass
    return job_id

def delete(job_id):
    with os.popen('qdel ' + job_id) as f:
        pass

def status():
    status_dict = {}
    with os.popen('qstat') as f:
        pass
    return status_dict

def job_stats(job_id):
    stats_dict = {}

    return stats_dict

def running_stats(job_id):
    stats_dict = {}

    return stats_dict

