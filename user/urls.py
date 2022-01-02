from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from user import views
from rest_framework_simplejwt import views as jwt_views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('login', views.UserLoginView.as_view()),
    path('register', views.UserRegisterView.as_view()),
    path('logout', views.UserLogoutView.as_view()),
    path('status', views.UserStatusView.as_view()),
    path('update', views.UserUpdateView.as_view()),
    path('delete', views.UserDeleteView.as_view()),
    path('token-refresh', jwt_views.TokenRefreshView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)