#!/usr/bin/env python2

import urllib
import urllib2
import argparse

class HerokuServiceClient:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def integrate(self, function, rangeFrom, rangeTo, steps):
        query_string = urllib.urlencode({'function': function,
                                         'from': rangeFrom,
                                         'to': rangeTo,
                                         'steps': steps})
        url = "{}/integrate?{}".format(self.endpoint, query_string)
        return float(urllib2.urlopen(url).read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("api", type=str, help="api endpoint")
    parser.add_argument("function", type=str, help="integrand")
    parser.add_argument("from", type=float, help="interval begin")
    parser.add_argument("to", type=float, help="interval end")
    parser.add_argument("steps", type=int, help="integration steps")
    args = vars(parser.parse_args())

    client = HerokuServiceClient(args['api'])
    integral = client.integrate(args['function'],
                                args['from'],
                                args['to'],
                                args['steps'])
    print integral
