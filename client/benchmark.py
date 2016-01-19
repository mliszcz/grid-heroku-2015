#!/usr/bin/env python2

import math
import time
import Queue
import threading
import itertools

from client import HerokuServiceClient

# statistics ##################################################################
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5

###############################################################################

fn_timer = time.time
# fnTimer = time.clock # measures CPU time - CPU is inactive during the request

def perform_test_series(client, requests, steps):
    start = fn_timer()
    for _ in itertools.repeat(None, requests):
        client.integrate('sin(x)', 0, 101*math.pi, steps)
    return (fn_timer() - start)

def perform_concurrent_requests(client, requests, steps, clients):

    threads = []
    queue = Queue.Queue()

    def fn_thread():
        time = perform_test_series(client, requests, steps)
        queue.put(time)

    for i in range(clients):
        t = threading.Thread(target=fn_thread)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    times = []
    while not queue.empty():
        times.append(queue.get())

    return times

def benchmark_single_increasing_steps(client, requests = 100):
    """testcase"""
    for steps in [1000*10**x for x in range(5)]:
        time = perform_test_series(client, requests, steps)
        print steps, requests, time, time/requests

def benchmark_concurrent_requests(client,
                                  requests = 100,
                                  steps = 100,
                                  max_clients = 16):
    """testcase"""
    for clients in range(1, max_clients + 1):
        times = perform_concurrent_requests(client, requests, steps, clients)
        times_mean = mean(times)
        times_stdev = 0 if len(times) == 1 else pstdev(times)
        print clients, times_mean, times_stdev
    pass


if __name__ == '__main__':
    endpoint = 'https://tranquil-journey-6372.herokuapp.com'
    # endpoint = 'http://localhost:8080'
    client = HerokuServiceClient(endpoint)

    # benchmark_concurrent_requests(client)
    benchmark_single_increasing_steps(client, 100)
