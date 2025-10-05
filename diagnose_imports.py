# diagnose_imports.py
import os, sys, importlib, traceback

print("cwd:", os.getcwd())
print("python exe:", sys.executable)
print("sys.path[0]:", sys.path[0])
print("dir listing:")
print(sorted(os.listdir(".")))
print("----- trying to import modules -----")

for name in ("models", "game"):
    try:
        m = importlib.import_module(name)
        print(f"import {name} OK -->", getattr(m, "__file__", "(no __file__)"))
    except Exception:
        print(f"ERROR importing {name}:")
        traceback.print_exc()
