"""
This module contains a custom decorator for db / redis mutexes
"""
import time
from uuid import uuid4
from django.core.cache import cache

LOCK_SECONDS = 30
INTERVAL = .5

def tree_mutex(name, interval=INTERVAL):
    lock_name = f"MUTEX_{name}_TREE"
    uuid = uuid4()

    def inner_function(f):
        def innermost_function(*args, **kwargs):
            #for n in range(int(LOCK_SECONDS/interval)):
            timeout = time.time() + LOCK_SECONDS
            while time.time() < timeout:
                # Attempt to acquire the mutex
                mutex = cache.get_or_set(lock_name, uuid, LOCK_SECONDS)
                # If our UUID was returned, we were successful!
                if mutex == uuid:
                    # Run the actual function
                    value = f(*args, **kwargs)
                    # Release the mutex
                    cache.delete(lock_name)
                    return value
                else:
                    time.sleep(interval)
        return innermost_function
    return inner_function
