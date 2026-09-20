"""Deployment: a minimal Python entry point.

Matches section 11 (PART C). Shipping this needs the right Python
interpreter, a virtualenv, and every dependency from pip installed
alongside it before it can start (~9 ms interpreter start-up).

Time the process start-up from the shell, for example:

    python -c "import time; s=time.perf_counter(); print('hello'); print(time.perf_counter()-s)"

or on Linux/macOS:

    time python 11-deployment/python/hello.py
"""

if __name__ == "__main__":
    print("hello")
