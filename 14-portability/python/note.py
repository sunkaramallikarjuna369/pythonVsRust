"""Portability: Python needs an interpreter wherever it runs.

Matches section 14 (PART C). Servers and PCs: fine, there is almost
always a Python already installed or easy to install. Browsers need a
heavy runtime (Pyodide/WASM build of CPython); tiny microcontrollers
only get a cut-down MicroPython, not full CPython.
"""
import platform
import sys


if __name__ == "__main__":
    print(f"running on {platform.system()} {platform.machine()}")
    print(f"needs: CPython {sys.version.split()[0]} interpreter present on this machine")
    print("browsers: would need Pyodide (a WASM build of CPython) to run at all")
    print("tiny embedded chips: only MicroPython (a cut-down reimplementation) fits")
