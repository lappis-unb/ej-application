import pytest
import mock
from ej_conversations.tools.mailing import TemplateGenerator
from ej_boards.mommy_recipes import BoardRecipes
from ej_conversations.tools.forms import MailingToolForm


class TestTemplateGenerator(BoardRecipes):
    def test_generate_vote_url(self, mk_user, conversation_db):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        request.POST = {"custom-domain": "http://ejplatform.local"}
        user = mk_user(email="test@domain.com")
        comment_1 = conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        generator = TemplateGenerator(conversation_db, request, "mautic")
        vote_url = generator._get_voting_url()

        expected_url = (
            "http://ejplatform.local/conversations/{}/{}"
            "?comment_id={}&action=vote&origin=campaign".format(
                conversation_db.id, conversation_db.slug, comment_1.id
            )
        )

        assert vote_url == expected_url

    def test_generate_vote_url_with_board(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        request.POST = {"custom-domain": "http://ejplatform.local"}
        board = mk_board()
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, "comment 1", "approved")
        board.add_conversation(conversation)
        generator = TemplateGenerator(conversation, request, "mautic")
        vote_url = generator._get_voting_url()

        expected_url = (
            "http://ejplatform.local/{}/conversations/{}/{}"
            "?comment_id={}&action=vote&origin=campaign".format(
                board.slug, conversation.id, conversation.slug, comment_1.id
            )
        )

        assert vote_url == expected_url

    def test_apply_default_palette_on_mail_template(self, mk_conversation, mk_board, mk_user):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        conversation = mk_conversation()
        user = mk_user(email="test2@domain.com")
        comment_1 = conversation.create_comment(user, "comment 1", "approved")
        generator = TemplateGenerator(conversation, request, "mautic")

        arrow = "border-top: 28px solid {} !important;".format("#C4F2F4")
        dark = "color: {} !important; background-color: {};".format("#C4F2F4", "#30BFD3")
        light = "color: {}; background-color: {};".format("#30BFD3", "#C4F2F4")
        expected_palette = {"arrow": arrow, "dark": dark, "light": light, "light-h1": "", "dark-h1": ""}

        palette = generator._get_palette_css()
        assert palette == expected_palette

    def test_apply_board_palette_on_campaign_template(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        board = mk_board(palette="orange")
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, "comment 1", "approved")
        board.add_conversation(conversation)
        generator = TemplateGenerator(conversation, request, "mautic", board.palette)

        arrow = "border-top: 28px solid {} !important;".format("#FFE1CA")
        dark = "color: {} !important; background-color: {};".format("#FFE1CA", "#F5700A")
        light = "color: {}; background-color: {};".format("#F5700A", "#FFE1CA")
        expected_palette = {"arrow": arrow, "dark": dark, "light": light, "light-h1": "", "dark-h1": ""}

        palette = generator._get_palette_css()
        assert palette == expected_palette

    def test_apply_campaign_palette_on_mail_template(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        board = mk_board(palette="campaign")
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, "comment 1", "approved")
        board.add_conversation(conversation)
        campaign = TemplateGenerator(conversation, request, "mautic", "campaign")

        arrow = "border-top: 28px solid {} !important;".format("#332f82")
        dark = "color: {} !important; background-color: {}; border-radius: unset;".format(
            "#332f82", "#1c9dd9"
        )
        light = "color: {}; background-color: {}; border-radius: unset;".format("#1c9dd9", "#332f82")
        expected_palette = {
            "arrow": arrow,
            "dark": dark,
            "light": light,
            "light-h1": "color: #ffffff !important;",
            "dark-h1": "color: #1c9dd9 !important;",
        }

        palette = campaign._get_palette_css()
        assert palette == expected_palette

    def test_set_custom_comment_template(self, mk_user, conversation_db):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        request.POST = {"custom-domain": "http://ejplatform.local"}
        user = mk_user(email="test@domain.com")
        comment_1 = conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        generator = TemplateGenerator(conversation_db, request, "mautic")
        generator.set_custom_values(None, comment_1)
        assert generator.comment.content == comment_1.content
        assert generator.comment == comment_1
        assert generator.conversation.text == conversation_db.text

    def test_set_custom_title_template(self, mk_user, conversation_db):
        request = mock.Mock()
        request.META = {"wsgi.url_scheme": "http", "HTTP_HOST": "ejplatform.local"}
        request.POST = {"custom-domain": "http://ejplatform.local"}
        new_title = "Text of the new title"
        user = mk_user(email="test@domain.com")
        conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        generator = TemplateGenerator(conversation_db, request, "mautic")
        generator.set_custom_values(new_title, None)
        assert generator.comment.content == conversation_db.approved_comments.last().content
        assert generator.comment == conversation_db.approved_comments.last()
        assert generator.conversation.text == new_title


class TestConversationComponentForm(BoardRecipes):
    def test_conversation_component_valid_mautic_form(self, conversation_db, mk_user):
        user = mk_user(email="test@domain.com")
        conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        form = MailingToolForm(
            {"template_type": "mautic", "theme": "default", "custom_title": None, "custom_comment": None},
            conversation_id=conversation_db.id,
        )
        assert form.is_valid()

    def test_conversation_component_valid_mautic_form(self, conversation_db, mk_user):
        user = mk_user(email="test@domain.com")
        conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        form = MailingToolForm(
            {"template_type": "mailchimp", "theme": "icd", "custom_title": None, "custom_comment": None},
            conversation_id=conversation_db.id,
        )
        assert form.is_valid()

    def test_conversation_component_valid_custom_attributes(self, conversation_db, mk_user):
        user = mk_user(email="test@domain.com")
        comment_1 = conversation_db.create_comment(user, "comment 1", status="approved", check_limits=False)
        form = MailingToolForm(
            {
                "template_type": "mailchimp",
                "theme": "icd",
                "custom_title": "New title",
                "custom_comment": comment_1.id,
            },
            conversation_id=conversation_db.id,
        )
        print(form.errors)
        assert form.is_valid()
