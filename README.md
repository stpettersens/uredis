### uredis
> Redis compatible server and client implemented in Python mostly using only the standard library.+

Latest version is v0.2.0 (WIP) and the following commands are implemented:

* HELLO
* INFO <<<
* CLIENT
* PING
* ECHO
* SET
* GET
* TTL
* DEL
* FLUSHDB
* FLUSHALL
* KEYS

The only data type supported so far is strings, but this version
is good enough to run my http://ip-locator.xyz application on FreeBSD.

+ We mostly use only the Python standard library but the [psutil module](https://pypi.org/project/psutil)
must be installed to return useful memory usage information with the INFO command. Otherwise, 0 bytes in process memory usage will be returned.
