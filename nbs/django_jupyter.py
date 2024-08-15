import os
import sys

DJANGO_SETTINGS_MODULE = "FlixFinder.settings"



def init():
    project_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_directory)
    
    # Set environment variables
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    
    import django
    django.setup()