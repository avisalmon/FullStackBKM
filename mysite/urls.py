"""Root URL configuration.

Order matters: each product app is mounted under its own prefix BEFORE the catch-all
`core.urls` include, so a prefix is unambiguously the app's own.
"""

from django.contrib import admin
from django.urls import include, path, re_path

from core.views import media_serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # --- your apps go here, one line each, e.g.:
    # path("recipes/", include("recipes.urls", namespace="recipes")),
    path("notes/", include("notes.urls", namespace="notes")),
    path("", include("core.urls")),
]

# Media is served by Django itself in every environment.
# DO NOT use django.conf.urls.static.static() here: it silently returns [] when
# DEBUG=False, so uploads 404 in production. Fine for a small site; move to object
# storage (S3 / R2 / Bunny) when traffic or file volume grows.
urlpatterns += [re_path(r"^media/(?P<path>.*)$", media_serve, name="media")]

handler404 = "core.views.not_found"
handler500 = "core.views.server_error"
