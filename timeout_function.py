import signal
import time
import sys
import multiprocessing
from typing import Callable


class TimeoutError(Exception):
    pass

def timer_handler(signum, frame):
    raise TimeoutError

def beautiful_function(q, sleep_time=1):
    print(f"going to sleep for {sleep_time}")
    time.sleep(sleep_time)
    print("finished sleeping")
    if q:
        q.put(sleep_time)


def timeout_tester_linux(sleep_time, target_function:Callable):
    """
    Signals work with linux so this function only runs on linux
    """
    signal.signal(signal.SIGALRM, timer_handler)
    signal.alarm(3)

    try:
        target_function(q=None, sleep_time=sleep_time)
    except TimeoutError:
        print("sanctioned function cause it sleeped to long")

def timeout_tester_windows(sleep_time: int, target_function:Callable):
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=target_function, args=[q, sleep_time])
    p.start()
    #timeout after 3 seconds
    p.join(3)
    try: 
        if p.is_alive():
            p.terminate()
            p.join()
            raise TimeoutError()
    except TimeoutError:
        print(f"sanctioned function {target_function.__name__} cause it sleeped too long: {p.exitcode}")
        return
    result = q.get_nowait()
    print(f"result: {result}")
    return p.exitcode

if __name__ == "__main__":
    if sys.platform == "linux":
        timeout_tester_linux(4, beautiful_function)
    elif sys.platform == "win32":
        timeout_tester_windows(5, beautiful_function)

