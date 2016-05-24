from __future__ import absolute_import
import os, sys

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core import management
    management.execute_from_command_line(sys.argv)
