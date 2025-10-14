from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from roulette import views as roulette_views

# Setup drf router
router = routers.DefaultRouter()
router.register(r"roulette", roulette_views.RouletteViewSet, basename="roulette")
router.register(
    r"participant",
    roulette_views.ParticipantViewSet,
    basename="participant",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirects
    path("", RedirectView.as_view(url="/admin/"), name="home-redirect-admin"),
    path(
        "accounts/login/",
        RedirectView.as_view(url="/admin/"),
        name="login-redirect-admin",
    ),
    # Crud endpoints
    path("api/", include(router.urls)),
]

if not settings.AWS_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
