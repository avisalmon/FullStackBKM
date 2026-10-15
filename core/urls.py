from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("healthz", views.healthz, name="healthz"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("ops/costs/", views.costs_page, name="costs"),
    path("internal/run/<slug:task>/", views.run_task, name="run_task"),
]
