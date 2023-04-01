"""Test script."""
# ruff: noqa: T201
import os
from pathlib import Path
from time import sleep

print(Path(os.path.curdir).resolve())

print("this is from test.py")

print("sleeping...")

sleep(10)

print("waked up")
