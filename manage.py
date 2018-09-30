#!/usr/bin/env python
import os
import sys
from hashlib import sha1 as sha_constructor

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canoba.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
