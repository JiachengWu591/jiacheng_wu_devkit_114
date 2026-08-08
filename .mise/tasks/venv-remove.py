# -*- coding: utf-8 -*-

"""
Remove the .venv directory (cross-platform equivalent of `rm -rf .venv`).
"""

import shutil

shutil.rmtree(".venv", ignore_errors=True)
