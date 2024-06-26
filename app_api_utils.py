import time
import functools
import random


def exponential_backoff(
        initial_delay=1.0,
        max_delay=32.0,
        max_retries=5,
        backoff_factor=2,
        exceptions=(Exception,),
):
    """
    Exponential backoff decorator.

    Args:
        initial_delay (float): The initial delay before the first retry.
        max_delay (float): The maximum delay between retries.
        max_retries (int): The maximum number of retries.
        backoff_factor (float): The factor by which the delay increases after each attempt.
    Returns:
        Decorator function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            attempt = 0

            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_retries:
                        raise
                    # Use a jitter to prevent thundering herd problem
                    sleep_time = delay + random.uniform(0, delay)
                    print(
                        f"Attempting function '{func.__name__}' Attempt {attempt} failed with {e.__class__.__name__}: {e}. Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    delay = min(delay * backoff_factor, max_delay)

        return wrapper

    return decorator

@exponential_backoff(initial_delay=20, max_delay=200, max_retries=10, backoff_factor=2)
def read_sheet(sh, worksheet_name):
    return sh.worksheet(worksheet_name)

@exponential_backoff(initial_delay=20, max_delay=200, max_retries=10, backoff_factor=2)
def read_row_values(sheet, row_index):
    return sheet.row_values(row_index)