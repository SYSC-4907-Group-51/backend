import threading

def run_task(task):
    """
    dict(
        target=do_something,
        args=(arg1,),
        daemon=True,
    )
    """
    thread = threading.Thread(**task)
    thread.start()

def run_tasks(tasks):
    for task in tasks:
        run_task(task)

def sleep_then_run_task(task, sleep_time):
    thread = threading.Timer(sleep_time, run_task, args=(task,))
    thread.start()