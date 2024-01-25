import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neuroprop.settings')

app = Celery('neuroprop')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


'''
Testing

run in seperate terminals...
redis-server   
and
celery -A neuroprop worker -l INFO

'''