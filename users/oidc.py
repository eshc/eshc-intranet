from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import User
from users.models import Profile
import unicodedata


def username_algo(email: str, claims: dict):
    return unicodedata.normalize("NFKC", claims["preferred_username"])[:150]


class ESHC_OIDCAB(OIDCAuthenticationBackend):
    def _fill_userdata(self, user: User, claims: dict):
        user.first_name = claims.get("first_name", "")
        user.last_name = claims.get("last_name", "")

        profile = user.profile

        profile.oidc_sub = claims.get("sub", None)
        profile.preferred_name = claims.get("preferred_name", None)
        profile.phone_number = claims.get("phone_number", None)
        profile.perm_address = claims.get("perm_address", None)

        user.is_superuser = claims.get("is_admin", False)

        profile.save()
        user.save()

    def create_user(self, claims):
        user = super(ESHC_OIDCAB, self).create_user(claims)

        self._fill_userdata(user, claims)
        return user

    def update_user(self, user, claims):
        self._fill_userdata(user, claims)
        return user

    # https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#connecting-oidc-user-identities-to-django-users
    # By default django-oidc matches a oidc user to django user the email claim
    # We use the sub claim instead, set when we create an account initally.
    # While the sub *can* change, depending on how the IdP is setup, it probably shouldnt.
    # E.g. if it is derived from the email
    def filter_users_by_claims(self, claims):
        sub = claims.get("sub")
        if not sub:
            return self.UserModel.objects.none()
        try:
            profile = Profile.objects.get(oidc_sub=sub)
            return [profile.user]

        except Profile.DoesNotExist:
            return self.UserModel.objects.none()
