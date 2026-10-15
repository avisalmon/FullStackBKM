from django.conf import settings


class PermissionsPolicyMiddleware:
    """Tell browsers this site never needs the camera, microphone, location or payment APIs.

    If a page does need one, widen PERMISSIONS_POLICY in settings for the whole site on purpose
    (and record why in docs/privacy_decisions.md). It also blocks third-party scripts you might
    add later from quietly using them.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault("Permissions-Policy", settings.PERMISSIONS_POLICY)
        return response
