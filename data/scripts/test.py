"""Test script."""
# ruff: noqa: T201
import os
from pathlib import Path
from time import sleep

from filetransferautomation.script import test

test()

print(Path(os.path.curdir).resolve())

print("this is from test.py")

print("sleeping...")

sleep(10)

print("waked up")
