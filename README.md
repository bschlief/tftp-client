A simple netascii-only tftp client in Python for getting files. Write requests not supported (yet).

Usage
-----

```
python client.py [-h] [-H HOST] [-p PORT] filename

positional arguments:
  filename

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  TFTP server hostname. Defaults to localhost.
  -p PORT, --port PORT  TFTP server port. Defaults to 69.
```

Testing
-------

```
pip install -r requirements.txt
python test.py
```