from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("ops/costs/", views.costs_page, name="costs"),
    path("internal/run/<slug:task>/", views.run_task, name="run_task"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("terms/", views.terms_page, name="terms"),
    path("privacy/my-data/", views.my_data, name="my_data"),
    path("privacy/my-data/export/", views.my_data_export, name="my_data_export"),
    path("privacy/my-data/delete/", views.my_data_delete, name="my_data_delete"),
]
