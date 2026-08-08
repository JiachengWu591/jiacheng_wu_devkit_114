# -*- coding: utf-8 -*-

"""
Remove the previously built Sphinx HTML output (cross-platform equivalent of `rm -rf docs/build`).
"""

import shutil

shutil.rmtree("docs/build", ignore_errors=True)
