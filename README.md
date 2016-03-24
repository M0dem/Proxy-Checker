# Proxy-Checker
Check a list of proxies and return the valid ones.
You can use Proxy Checker as a library or CLI.

If you find any bugs, please contact me.

# Requirements:
 - **requests** (HTTP library)

# Usage
```python
 ProxyChecker(inlist, threads = 200, verbose = False, timeout = 25)
```
######Example usage:
```python
 from proxychecker import ProxyChecker
 proxy_checker = ProxyChecker(myproxylist, timeout = 20)
 outlist = proxy_checker.start()
```
****
To use the CLI, directly execute `proxychecker.py` on the command line.
######Example usage:
```
 python proxychecker.py -h
```
