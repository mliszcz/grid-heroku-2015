#!/usr/bin/env python2

import math
import time
import itertools

from client import HerokuServiceClient

fnTimer = time.time
# fnTimer = time.clock # measures CPU time - CPU is inactive during the request

def perform_test_series(client, requests, steps):
    start = fnTimer()
    for _ in itertools.repeat(None, requests):
        client.integrate('sin(x)', 0, 101*math.pi, steps)
    return (fnTimer() - start)

def benchmark_single_increasing_steps(client, requests = 100):
    for steps in [1000*10**x for x in range(5)]:
    # for steps in [1000*(x+1) for x in range(20)]:
        time = perform_test_series(client, requests, steps)
        print steps, requests, time, time/requests

if __name__ == '__main__':
    # endpoint = 'http://tranquil-journey-6372.herokuapp.com'
    endpoint = 'http://localhost:8080'
    client = HerokuServiceClient(endpoint)

    benchmark_single_increasing_steps(client, 100)
