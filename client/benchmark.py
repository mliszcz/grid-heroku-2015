#!/usr/bin/env python2

from client import HerokuServiceClient

if __name__ == '__main__':
    endpoint = 'http://tranquil-journey-6372.herokuapp.com'
    client = HerokuServiceClient(endpoint)
    print client.integrate('sin(x)+2', 0, 1, 100)
