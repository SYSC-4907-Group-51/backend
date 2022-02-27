from django.urls import path
from user import views
from rest_framework_simplejwt import views as jwt_views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('login', views.UserLoginView.as_view()), # /login
    path('register', views.UserRegisterView.as_view()), # /register
    path('logout', views.UserLogoutView.as_view()), # /logout
    path('status', views.UserStatusView.as_view()), # /status
    path('sync-status', views.UserSyncStatusView.as_view()), # /sync-status
    path('update', views.UserUpdateView.as_view()), # /update
    path('delete', views.UserDeleteView.as_view()), # /delete
    path('logs', views.LogView.as_view()), # /logs
    path('token-refresh', jwt_views.TokenRefreshView.as_view()), # /token-refresh
]