import os

import django
from django.test import SimpleTestCase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.django.django_settings')

django.setup()
MagicBoxTestCase = SimpleTestCase
