# -*- coding: utf-8 -*-

from jiacheng_wu_devkit_114 import api


def test():
    _ = api


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.api",
        preview=False,
    )
