from logging import getLogger

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from . import models
from .exceptions import ApiError
from .rocket import rocket

log = getLogger('ej')
User = get_user_model()


class RocketIntegrationForm(forms.Form):
    """
    Form that asks basic configuration about a Rocket.Chat instance.
    """

    rocketchat_url = forms.URLField(
        label=_('Rocket.Chat URL'),
        help_text=_('Required URL for Rocket.Chat admin instance.'),
        initial=settings.EJ_ROCKETCHAT_URL,
    )
    admin_username = forms.CharField(
        label=_('Username'),
        help_text=_('Username for Rocket.Chat admin user.')
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_('Password'),
        help_text=_('Password for Rocket.Chat admin user.')
    )
    config = None

    def get_config(self):
        """
        Return Rocket.Chat config from form data.
        """
        if self.config is None:
            return self._clean_config()
        else:
            return self.config

    def full_clean(self):
        super().full_clean()

        try:
            self._clean_config(self.cleaned_data)
        except (AttributeError, ImproperlyConfigured, KeyError):
            pass

    def _clean_config(self, data):
        """
        Return a saved RCConfig instance from form data.
        """
        url = data['rocketchat_url']
        config = models.RCConfig(url=url)
        response = config.api_call(
            'login',
            payload={
                'username': data['admin_username'],
                'password': data['admin_password'],
            },
            raises=False,
        )
        if response.get('status') == 'success':
            self.config = self._save_config(response['data'])
            self._save_admin_account(self.config)
            return config
        else:
            raise ValueError(response)

    def _save_config(self, data):
        url = self.cleaned_data['rocketchat_url']
        user_id = data['userId']
        auth_token = data['authToken']

        # Save config
        config, _ = models.RCConfig.objects.get_or_create(url=url)
        config.admin_id = user_id
        config.admin_token = auth_token
        config.is_active = True
        config.save()
        return config

    def _save_admin_account(self, config):
        response = config.api_call(
            'users.info',
            args={'userId': config.admin_id},
            auth='admin',
            method='get',
        )
        emails = [mail['address'] for mail in response['emails']]
        for email in emails:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                continue

            return models.RCAccount.objects.create(
                config=config,
                user=user,
                user_rc_id=config.admin_id,
                auth_token=config.admin_token,
                username=self.cleaned_data['admin_username'],
                password='',
            )


class CreateUsernameForm(forms.ModelForm):
    """
    Asks user for a new username for its Rocket.Chat account.
    """

    class Meta:
        model = models.RCAccount
        fields = ['username']

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def full_clean(self):
        super().full_clean()
        try:
            username = self.cleaned_data['username'].lstrip('@')
        except (KeyError, AttributeError):
            return
        try:
            self.instance = rocket.register(self.user, username)
        except ApiError as error:
            msg = error.args[0]
            error = msg.get('error', '')
            if f'{username} is already in use' in error:
                self.add_error('username', _('Username already in use.'))
            elif f'{self.user.email} is already in use' in error:
                email = self.user.email
                msg = _(f'User with {email} e-mail already exists.')
                self.add_error('username', msg)
            else:
                raise
        else:
            rocket.login(self.user)


class AskAdminPasswordForm(forms.Form):
    """
    Asks EJ superusers for the Rocket.Chat admin user password.
    """
    password = forms.CharField(
        label=_('Password'),
        help_text=_('Password for the Rocket.Chat admin account'),
        widget=forms.PasswordInput,
    )

    def full_clean(self):
        super().full_clean()
        if self.is_valid():
            password = self.cleaned_data['password']
            try:
                rocket.password_login(rocket.admin_username, password)
            except PermissionError:
                self.add_error('password', _('Invalid password'))
