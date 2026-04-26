import os
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
from django.core.wsgi import get_wsgi_application

django.setup()
application = get_wsgi_application()
