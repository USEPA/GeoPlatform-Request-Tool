#!/usr/bin/env python
import os
import sys
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AGOLAccountRequestor.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # try:
    execute_from_command_line(sys.argv)
    # except Exception as e:
    #     logger.error('Command Error: {}'.format(' '.join(sys.argv)), exc_info=sys.exc_info())
