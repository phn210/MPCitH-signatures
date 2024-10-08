import timeit
from functools import wraps
from utils.log.table import log_table_from_rows

profile = {}

def benchmark(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global profile
        start_time = timeit.default_timer()     # Record the start time
        result = func(*args, **kwargs)          # Call the original function with its arguments
        end_time = timeit.default_timer()       # Record the end time
        execution_time = end_time - start_time  # Calculate execution time
        if func.__name__ not in profile.keys():
            profile.update({func.__name__: {"num_calls": 0, "total_time": 0, "avg_time": 0}})
        total_time = profile[func.__name__]["total_time"] + execution_time
        num_calls = profile[func.__name__]["num_calls"] + 1
        avg_time = total_time / num_calls
        profile[func.__name__] = {
            "total_time": total_time,
            "avg_time": avg_time,
            "num_calls": num_calls,
        }
        return result
    return wrapper


def log():
    headers = ["Function", "Number of Calls", "Total Time", "Average Time"]
    rows = []
    for func, stats in profile.items():
        rows.append([func, stats["num_calls"], stats["total_time"], stats["avg_time"]])
    log_table_from_rows(headers, rows)


def reset():
    profile.clear()


def get(key):
    if key in profile.keys():
        return profile[key]