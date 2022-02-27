from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker import views

# Create a router and register our viewsets with it.
router = DefaultRouter()

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('auth', views.TrackerAuthorizeView.as_view()), # /auth
    path('refresh', views.TrackerRefreshView.as_view()), # /refresh
    path('delete', views.TrackerDeleteView.as_view()), # /delete
    path('', include(router.urls)),
]