from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ej_conversations import create_conversation
from ej_clusters.models import Clusterization
from ej_clusters.tasks import update_clusterization

User = get_user_model()

class CeleryTaskIntegrationTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="test_user",
            email="test_user@example.com",
            password="password"
        )

        # Use create_conversation utility function to create a test conversation
        self.conversation = create_conversation(
            text="Test conversation text",
            title="Test Conversation",
            author=self.user,
            board=None,
            is_promoted=False,
            tags="",
            commit=True
        )

        # Create a test clusterization
        self.clusterization = Clusterization.objects.create(
            conversation=self.conversation
        )

    def test_update_clusterization_task(self):
        # Enqueue the task
        result = update_clusterization.delay(self.clusterization.id)

        # Wait for the task to complete
        task_result = result.get(timeout=20)

        # Refresh the clusterization object from the database
        self.clusterization.refresh_from_db()

        # Check the task result and clusterization status
        self.assertEqual(task_result, "Clusterization updated")
        self.assertEqual(self.clusterization.cluster_status, "ACTIVE")

    def test_celery_task_execution(self):
        # Test if the Celery worker is running and can execute a simple task
        from ej_clusters.tasks import test_celery

        # Enqueue the task
        result = test_celery.delay()

        # Wait for the task to complete
        task_result = result.get(timeout=10)

        # Check the task result
        self.assertTrue(task_result, "Celery is working!")

    def tearDown(self):
        self.conversation.delete()
        self.clusterization.delete()
        self.user.delete()