from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """

    def _make_hash_value(self, user, timestamp):
        """Return a token to confirm email."""
        return f"{text_type(user.pk)}{text_type(timestamp)}{text_type(user.email_confirmed)}"


account_activation_token = AccountActivationTokenGenerator()
