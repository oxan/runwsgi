# runwsgi: Simple WSGI development server

runwsgi is a simple WSGI development server with support for hot reloading,
based upon [wsgiref].

## Usage

Run `runwsgi` with the filename or module name of your application:

```python
# my_wsgi_app.py
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Hello world']
```

```
$ runwsgi --port 8080 my_wsgi_app.py
```

The HTTP port can also be specified using `-p` or left out, in which case port
8000 is used. You can use a virtualenv by running `runwsgi` with the Python from
inside the virtualenv.

## Hot reload

runwsgi automatically reloads any modules imported from the application
directory (and subdirectories) when they are modified. Note that reloading is
done using the [importlib.reload] function, and its documented caveats apply to
runwsgi as well. Most notably this means that anything imported using the
 `from ... import ...` syntax will not be redefined on reload, and the old
version will still be used.

[wsgiref]: https://docs.python.org/3/library/wsgiref.html#module-wsgiref.simple_server
[importlib.reload]: https://docs.python.org/3/library/importlib.html#importlib.reload
