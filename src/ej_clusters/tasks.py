from .models import Clusterization
from celery import shared_task


@shared_task
def update_clusterization(id):
    """
    Task that fetches a clusterization with the given id and executes it's
    .update_clusterization() method.
    """
    clusterization = Clusterization.objects.filter(id=id).first()
    if clusterization is not None:
        clusterization.update_clusterization()


@shared_task
def test_celery():
    print("Celery is working!")
