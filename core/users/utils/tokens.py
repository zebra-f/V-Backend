from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivateUserTokenGenerator(PasswordResetTokenGenerator):

    def check_token(self, user, token):
        if user.is_active:
            return False
        return super().check_token(user, token)


class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    pass


activate_user_token_generator = ActivateUserTokenGenerator()
custom_password_reset_token_generator = CustomPasswordResetTokenGenerator()