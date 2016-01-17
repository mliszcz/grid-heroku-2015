# grid-heroku-2015

## Client

Client script is stored in the `client/client.py` file.
It may be used as a standalone application or loaded as a Python module.

### Standalone mode

```
$ ./client.py 'http://tranquil-journey-6372.herokuapp.com' 'sin(x)+1' 0 1 100
1.45969960954
```

```
$ ./client.py -h
usage: client.py [-h] api function from to steps

positional arguments:
  api         api endpoint
  function    integrand
  from        interval begin
  to          interval end
  steps       integration steps

optional arguments:
  -h, --help  show this help message and exit
```

### Library mode

```python
#!/usr/bin/env python2

from client import HerokuServiceClient

if __name__ == '__main__':
    endpoint = 'http://tranquil-journey-6372.herokuapp.com'
    client = HerokuServiceClient(endpoint)
    print client.integrate('sin(x)+2', 0, 1, 100)
```
