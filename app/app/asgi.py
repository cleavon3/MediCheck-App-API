"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
>>>>>>> 369e8ce0160255d438b75c1fc3a65773cce11eae

application = get_asgi_application()
