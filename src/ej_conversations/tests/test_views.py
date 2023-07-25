from django.test import Client
from django.http import HttpResponseServerError, Http404
from pytest import raises
import pytest
import json
from ej_boards.models import Board

from ej_conversations import create_conversation, views
from ej_conversations.views import ConversationView
from ej_conversations.models import Comment, FavoriteConversation
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_conversations.utils import votes_counter
from ej_users.models import User
from ..enums import Choice


class TestConversationDetail:
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.fixture
    def first_conversation(self, admin_user):
        board = Board.objects.create(slug="board", owner=admin_user, description="board")
        conversation = create_conversation("foo", "conv1", admin_user, board=board)
        conversation.create_comment(admin_user, "ad", status="approved", check_limits=False)
        conversation.create_comment(admin_user, "ad2", status="approved", check_limits=False)
        conversation.is_promoted = True
        conversation.is_hidden = False
        conversation.save()
        return conversation

    def test_vote_agree_in_comment(self, first_conversation):
        User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        comment = first_conversation.comments.first()
        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "vote", "vote": "agree", "comment_id": comment.id},
        )

        assert response.context["conversation"] == first_conversation
        assert votes_counter(comment) == 1

        vote = comment.votes.first()
        assert vote.choice == Choice.AGREE

    def test_vote_disagree_in_comment(self, first_conversation):
        User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        comment = first_conversation.comments.first()
        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "vote", "vote": "disagree", "comment_id": comment.id},
        )
        assert response.context["conversation"] == first_conversation
        assert votes_counter(comment) == 1

        vote = comment.votes.first()
        assert vote.choice == Choice.DISAGREE

    def test_vote_skip_in_comment(self, first_conversation):
        User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        comment = first_conversation.comments.first()
        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "vote", "vote": "skip", "comment_id": comment.id},
        )
        assert response.context["conversation"] == first_conversation
        assert votes_counter(comment) == 1

        vote = comment.votes.first()
        assert vote.choice == Choice.SKIP

    def test_invalid_vote_in_comment(self, first_conversation):
        User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        comment = first_conversation.comments.first()
        with raises(Exception):
            client.post(
                f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
                {"action": "vote", "vote": "INVALID", "comment_id": comment.id},
            )

    def test_invalid_action_conversation_detail(self, first_conversation):
        User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        comment = first_conversation.comments.first()

        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "invalid", "vote": "INVALID", "comment_id": comment.id},
        )
        assert isinstance(response, HttpResponseServerError)

    def test_user_can_comment(self, first_conversation):
        user = User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "comment", "content": "test comment"},
        )

        assert Comment.objects.filter(author=user)[0].content == "test comment"

    def test_user_post_invalid_comment(self, first_conversation):
        user = User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "comment", "content": ""},
        )

        assert not Comment.objects.filter(author=user).exists()

    def test_anonymous_user_cannot_participate(self, first_conversation):
        client = Client()
        comment = first_conversation.comments.first()

        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "vote", "vote": "agree", "comment_id": comment.id},
        )
        assert response.status_code == 302
        assert (
            response.url
            == f"/login/?next=/board/conversations/{first_conversation.id}/{first_conversation.slug}/"
        )

        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "comment", "content": "test comment"},
        )
        assert response.status_code == 302
        assert (
            response.url
            == f"/login/?next=/board/conversations/{first_conversation.id}/{first_conversation.slug}/"
        )

        response = client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "favorite"},
        )
        assert response.status_code == 302
        assert (
            response.url
            == f"/login/?next=/board/conversations/{first_conversation.id}/{first_conversation.slug}/"
        )

    def test_user_can_add_conversation_as_favorite(self, first_conversation):
        user = User.objects.create_user("user@server.com", "password")

        client = Client()
        client.login(email="user@server.com", password="password")

        client.post(
            f"/board/conversations/{first_conversation.id}/{first_conversation.slug}/",
            {"action": "favorite"},
        )

        assert FavoriteConversation.objects.filter(user=user, conversation=first_conversation).exists()


class TestConversationComments:
    @pytest.mark.skip(reason="No revised test")
    def test_user_can_get_all_his_comments(self, request_with_user, conversation, user, comment):
        ctx = views.comment_list(request_with_user, conversation)
        assert len(ctx["approved"]) == 1
        assert len(ctx["rejected"]) == 0
        assert len(ctx["pending"]) == 0
        assert ctx["can_edit"]
        assert ctx["can_comment"]

    @pytest.mark.skip(reason="No revised test")
    def test_user_can_get_detail_of_a_comment(self, conversation, comment):
        ctx = views.comment_detail(conversation, comment)
        assert ctx["comment"] is comment

    @pytest.mark.skip(reason="No revised test")
    def test_comment_list_not_promoted_convesation(self, request_with_user, conversation, user):
        conversation.is_promoted = False
        with raises(Http404):
            views.comment_list(request_with_user, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_udetail_of_a_comment_not_promoted(self, conversation, comment):
        conversation.is_promoted = False
        with raises(Http404):
            views.comment_detail(conversation, comment)


class TestAdminViews(ConversationRecipes):
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.mark.skip(reason="No revised test")
    def test_create_conversation(self, rf, user):
        request = rf.post(
            "", {"title": "whatever", "tags": "tag", "text": "description", "comments_count": 0}
        )
        request.user = user
        response = views.create(request)
        assert response.status_code == 302
        assert response.url == "/conversations/whatever/stereotypes/"

    @pytest.mark.skip(reason="No revised test")
    def test_create_invalid_conversation(self, rf, user):
        request = rf.post("", {"title": "", "tags": "tag", "text": "description", "comments_count": 0})
        request.user = user
        response = views.create(request)
        assert not response["form"].is_valid()

    @pytest.mark.skip(reason="No revised test")
    def test_edit_conversation(self, rf, conversation):
        request = rf.post(
            "", {"title": "whatever", "tags": "tag", "text": "description", "comments_count": 0}
        )
        request.user = conversation.author
        response = views.edit(request, conversation)
        assert response.status_code == 302
        assert response.url == "/conversations/title/moderate/"

    @pytest.mark.skip(reason="No revised test")
    def test_edit_invalid_conversation(self, rf, conversation):
        request = rf.post("", {"title": "", "tags": "tag", "text": "description", "comments_count": 0})
        request.user = conversation.author
        response = views.edit(request, conversation)
        assert not response["form"].is_valid()

    @pytest.mark.skip(reason="No revised test")
    def test_edit_not_promoted_conversation(self, rf, conversation):
        request = rf.post("", {})
        request.user = conversation.author
        conversation.is_promoted = False
        with raises(Http404):
            views.edit(request, conversation)

    @pytest.mark.skip(reason="No revised test")
    def test_get_edit_conversation(self, rf, conversation):
        user = conversation.author
        comment = conversation.create_comment(user, "comment", "pending")
        conversation.create_comment(user, "comment1")
        comment.status = comment.STATUS.pending
        comment.save()
        request = rf.get("", {})
        request.user = user
        conversation.refresh_from_db()
        response = views.edit(request, conversation)
        assert response["comments"][0] == comment
        assert response["conversation"] == conversation

    def test_admin_can_moderate_comments(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment_to_approve = conversation.create_comment(
            author=user, content="comment to approve", status="pending"
        )
        comment_to_reject = conversation.create_comment(
            author=user, content="comment to reject", status="pending"
        )
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/moderate/"
        client.post(url, {"approved": comment_to_approve.id, "rejected": comment_to_reject.id})

        assert (
            conversation.comments.get(id=comment_to_approve.id).status == comment_to_approve.STATUS.approved
        )
        assert (
            conversation.comments.get(id=comment_to_reject.id).status == comment_to_reject.STATUS.rejected
        )

    def test_admin_can_create_comments(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comments = ["Some comment to test", "Some other comment to test"]
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/new/"
        client.post(url, {"comment": comments})

        assert Comment.objects.get(content=comments[0], author=user).status == "approved"
        assert Comment.objects.get(content=comments[1], author=user).status == "approved"

    def test_comments_with_less_than_2_chars_arent_created(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comments = ["A", "Some other comment to test"]
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/new/"
        client.post(url, {"comment": comments})

        assert Comment.objects.get(content=comments[1], author=user).status == "approved"
        assert Comment.objects.all().count() == 1

    def test_admin_can_delete_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment = conversation.create_comment(author=user, content="comment to delete", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/delete/"
        client.post(url, {"comment_id": comment.id})

        assert Comment.objects.all().count() == 0

    def test_admin_cant_delete_others_users_comments(self, logged_admin):
        user_1 = User.objects.create_user("user1@email.br", "password")
        user_2 = User.objects.create_user("user2@email.br", "password2")
        board = Board.objects.create(slug="board1", owner=user_1, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user_2, board=board)
        comment = conversation.create_comment(
            author=user_2, content="comment to not delete", status="approved"
        )
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/delete/"
        client.post(url, {"comment_id": comment.id})

        assert Comment.objects.all().count() == 1

    def test_admin_can_check_for_repeated_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        comment = conversation.create_comment(author=user, content="comment to check", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/check/"
        response = client.post(url, {"comment_content": "comment to check"})

        assert response.status_code == 200

    def test_admin_can_check_for_not_repeated_comment(self, logged_admin):
        user = User.objects.create_user("user1@email.br", "password")
        board = Board.objects.create(slug="board1", owner=user, description="board")
        client = Client()
        client.login(email="user1@email.br", password="password")
        conversation = create_conversation("foo", "conv1", user, board=board)
        conversation.create_comment(author=user, content="comment to check", status="approved")
        url = f"/{board.slug}/conversations/{conversation.id}/{conversation.slug}/comments/check/"
        response = client.post(url, {"comment_content": "new and different comment to check"})

        assert response.status_code == 204


class TestPrivateConversations(ConversationRecipes):
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        profile = admin_user.get_profile()
        profile.completed_tour = True
        profile.save()
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.fixture
    def base_user(self, db):
        user = User.objects.create_user("tester@email.br", "password")
        profile = user.get_profile()
        profile.completed_tour = True
        profile.save()
        return user

    @pytest.fixture
    def base_board(self, base_user):
        board = Board.objects.create(slug="userboard", owner=base_user, description="board")
        return board

    @pytest.fixture
    def hiden_conversation(self, admin_user):
        board = Board.objects.create(slug="adminboard", owner=admin_user, description="board")
        conversation = create_conversation("foo", "conv", admin_user, board=board)
        conversation.is_hidden = True
        conversation.save()
        return conversation

    @pytest.fixture
    def first_conversation(self, base_board, base_user):
        conversation = create_conversation("bar", "conv1", base_user, board=base_board)
        conversation.is_hidden = False
        conversation.save()
        return conversation

    @pytest.fixture
    def second_conversation(self, base_board, base_user):
        conversation = create_conversation("forbar", "conv2", base_user, board=base_board)
        conversation.is_hidden = False
        conversation.save()
        return conversation

    @pytest.fixture
    def third_conversation(self, base_board, base_user):
        conversation = create_conversation("forbarbar", "conv3", base_user, board=base_board)
        conversation.is_hidden = True
        conversation.save()
        return conversation

    def test_redirect_if_tour_is_imcoplete(
        self, logged_admin, base_board, hiden_conversation, first_conversation, second_conversation
    ):
        user = User.objects.create_user("test_user@email.br", "password")
        Board.objects.create(slug="secondboard", owner=user, description="board")

        url = "/secondboard/conversations/"
        client = Client()
        client.force_login(user)

        response = client.get(url)

        assert response.status_code == 302
        assert response.url == "/secondboard/conversations/tour"

    def test_user_can_access_their_board_conversations(
        self,
        logged_admin,
        base_board,
        hiden_conversation,
        first_conversation,
        second_conversation,
        third_conversation,
    ):
        user_url = f"/userboard/conversations/"

        client = Client()
        client.login(email="tester@email.br", password="password")
        response = client.get(user_url)

        assert len(response.context["conversations"]) == 2
        assert first_conversation in response.context["conversations"]
        assert second_conversation in response.context["conversations"]
        assert len(response.context["user_boards"]) == 2
        assert base_board in response.context["user_boards"]

        admin_url = "/adminboard/conversations/"
        response = logged_admin.get(admin_url)

        assert len(response.context["conversations"]) == 1
        assert hiden_conversation in response.context["conversations"]

    def test_anonymous_user_should_not_access_board_conversations(
        self, admin_user, base_user, hiden_conversation, first_conversation, second_conversation
    ):
        admin_url = f"/adminboard/conversations/"
        anonymous_user = Client()
        response = anonymous_user.get(admin_url)
        assert response.status_code == 302
        assert response.url == "/login/?next=/adminboard/conversations/"

    def test_only_admin_user_can_access_others_conversations(
        self, logged_admin, base_user, hiden_conversation, first_conversation, second_conversation
    ):
        user_url = f"/userboard/conversations/"
        response = logged_admin.get(user_url)

        assert len(response.context["conversations"]) == 2
        assert first_conversation in response.context["conversations"]
        assert second_conversation in response.context["conversations"]

        admin_url = f"/adminboard/conversations/"
        client = Client()
        client.login(email="tester@email.br", password="password")
        response = client.get(admin_url)
        assert response.status_code == 302
        assert response.url == "/login/"


class TestPublicConversations(ConversationRecipes):
    @pytest.fixture
    def admin_user(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        return admin_user

    @pytest.fixture
    def logged_admin(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        return client

    @pytest.fixture
    def promoted_conversation(self, admin_user):
        board = Board.objects.create(slug="board1", owner=admin_user, description="board")
        conversation = create_conversation("foo", "conv1", admin_user, board=board)
        conversation.is_promoted = True
        conversation.is_hidden = False
        conversation.save()
        return conversation

    @pytest.fixture
    def not_promoted_conversation(self, admin_user):
        board = Board.objects.create(slug="board2", owner=admin_user, description="board2")
        conversation = create_conversation("bar", "conv2", admin_user, board=board)
        conversation.is_promoted = False
        conversation.is_hidden = False
        conversation.save()
        return conversation

    @pytest.fixture
    def hiden_conversation(self, admin_user):
        board = Board.objects.create(slug="board3", owner=admin_user, description="board3")
        conversation = create_conversation("foobar", "conv3", admin_user, board=board)
        conversation.is_promoted = True
        conversation.is_hidden = True
        conversation.save()
        return conversation

    def test_authenticated_user_can_access_public_conversations(
        self, logged_admin, promoted_conversation, not_promoted_conversation, hiden_conversation
    ):
        url = f"/conversations/"
        response = logged_admin.get(url)

        board1 = Board.objects.get(slug="admintestcom")
        board2 = Board.objects.get(slug="board1")
        board3 = Board.objects.get(slug="board2")
        board4 = Board.objects.get(slug="board3")

        assert response.status_code == 200

        assert board1 in response.context["user_boards"]
        assert board2 in response.context["user_boards"]
        assert board3 in response.context["user_boards"]
        assert board4 in response.context["user_boards"]
        assert len(response.context["user_boards"]) == 4

        assert response.context["conversations_limit"] == 20

        assert promoted_conversation in response.context["conversations"]
        assert not_promoted_conversation not in response.context["conversations"]
        assert hiden_conversation in response.context["conversations"]

    def test_anonymous_user_can_access_public_conversations(
        self, logged_admin, promoted_conversation, not_promoted_conversation, hiden_conversation
    ):
        url = f"/conversations/"
        client = Client()
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["user_boards"] == []
        assert response.context["conversations_limit"] == 0
        assert promoted_conversation in response.context["conversations"]
        assert not_promoted_conversation not in response.context["conversations"]
        assert hiden_conversation not in response.context["conversations"]
