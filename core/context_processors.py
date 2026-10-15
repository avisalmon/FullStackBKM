from django.conf import settings


def site(request):
    """Values every site-level template needs."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "GOOGLE_LOGIN_ENABLED": settings.GOOGLE_LOGIN_ENABLED,
        "PLAUSIBLE_DOMAIN": settings.PLAUSIBLE_DOMAIN,
    }
