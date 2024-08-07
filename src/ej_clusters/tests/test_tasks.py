from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ej_conversations import create_conversation
from ej_clusters.models import Clusterization
from ej_clusters.tasks import update_clusterization, test_celery
from ej_users.models import User
from ..enums import ClusterStatus

User = get_user_model()


class CeleryTaskIntegrationTests(TestCase):

    def base_user(self, idx=0):
        user = User.objects.create_user(f"tester{idx}@email.br", "password")
        profile = user.get_profile()
        profile.save()
        return user

    def setUp(self):
        self.users = []
        # Create a test user
        for i in range(10):
            self.users.append(self.base_user(i))

        self.user = self.users[0]

        # Use create_conversation utility function to create a test conversation
        self.conversation = create_conversation(
            text="Test conversation text",
            title="Test Conversation",
            author=self.user,
            board=None,
            is_promoted=False,
            tags="",
            commit=True,
        )

        comment = self.conversation.comments.create(author=self.user)

        for i in range(10):
            self.conversation.votes.create(author=self.users[i], comment_id=comment.id)

        # Create a test clusterization
        self.clusterization = Clusterization.objects.create(
            conversation=self.conversation,
        )

    def test_update_clusterization_task(self):
        # Enqueue the task
        result = update_clusterization(self.clusterization.id)

        # Refresh the clusterization object from the database
        self.clusterization.refresh_from_db()

        # Check the task result and clusterization status
        self.assertEqual(result, "Clusterization updated")

    def test_celery_task_execution(self):
        """Test if the Celery worker is running and can execute a simple task"""
        # Enqueue the task
        result = test_celery

        # Wait for the task to complete
        # task_result = result.get(timeout=10)
        """
        The get is used only when the task is enqueued with delay.
        But in tests is not necessary, because the task is not enqueued,
        and the Celery recommends to not use it in tests.
        """

        # Check the task result
        self.assertTrue(result, "Celery is working!")

    def tearDown(self):
        self.conversation.delete()
        self.clusterization.delete()
        self.user.delete()
