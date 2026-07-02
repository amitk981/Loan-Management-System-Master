from django.urls import path

from sfpcl_credit.ops import deep_health, live_health, ready_health


urlpatterns = [
    path("api/v1/health/live/", live_health, name="health-live"),
    path("api/v1/health/ready/", ready_health, name="health-ready"),
    path("api/v1/health/deep/", deep_health, name="health-deep"),
]
