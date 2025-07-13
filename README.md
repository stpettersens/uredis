### uRedis
> Redis compatible server and client implemented in Python.

Latest version is v0.2.0 (WIP) and the following commands are implemented:

* HELLO
* INFO (since v0.2.0) †
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
* QUIT (since v0.2.0; TODO)

The only data type supported so far is strings, but this version
is good enough to run my http://ip-locator.xyz application on FreeBSD.

† uRedis is mostly implemented using the [Python standard library](https://docs.python.org/3/library/index.html) but uses
[psutil](https://pypi.org/project/psutil) and [Pymple](https://pypi.org/project/Pympler)
for memory information with the INFO command.

If you don't care about the INFO command, uRedis can be run without installing these dependencies.
