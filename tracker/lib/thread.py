import threading

def run_task(task):
    """
        Create a thread to run a background task

        Args:
            task: dict, threading.Thread parameters
                dict(
                    target=do_something,
                    args=(arg1,),
                    daemon=True,
                )
    """
    thread = threading.Thread(**task)
    thread.start()

def run_tasks(tasks):
    """
        Create a thread to run background tasks

        Args:
            task: list, threading.Thread parameters
                [
                    dict(
                        target=do_something,
                        args=(arg1,),
                        daemon=True,
                    ),
                    ...
                ]
    """
    for task in tasks:
        run_task(task)

def sleep_then_run_task(task, sleep_time):
    """
        Create a thread to run after specific time

        Args:
            task: dict, threading.Thread parameters
                dict(
                    target=do_something,
                    args=(arg1,),
                    daemon=True,
                )
            sleep_time: int, sleep time in sec
    """
    thread = threading.Timer(sleep_time, run_task, args=(task,))
    thread.start()