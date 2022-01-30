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