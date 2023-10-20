import signal
import time
import sys
import multiprocessing

class TimeoutError(Exception):
    pass

def timer_handler(signum, frame):
    raise TimeoutError

def beautiful_function(sleep_time=1):
    print(f"going to sleep for {sleep_time}")
    time.sleep(sleep_time)
    print("finished sleeping")


def timeout_tester_linux(sleep_time):
    """
    Signals work with linux so this function only runs on linux
    """
    signal.signal(signal.SIGALRM, timer_handler)
    signal.alarm(3)

    try:
        beautiful_function(sleep_time)
    except TimeoutError:
        print("sanctioned functi cause it sleeped to long")

def timeout_tester_windows(sleep_time):
    p = multiprocessing.Process(target=beautiful_function, args=[sleep_time])
    p.start()
    #timeout after 3 seconds
    p.join(3)
    try: 
        if p.is_alive():
            p.terminate()
            p.join()
            raise TimeoutError()
    except TimeoutError:
        print(f"sanctioned functi cause it sleeped to long: {p.exitcode=}")
    return p.exitcode

if __name__ == "__main__":
    if sys.platform == "linuxi":
        timeout_tester_linux(4)
    elif sys.platform == "linux": # "win32"
        timeout_tester_windows(5)

