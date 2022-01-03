from django.urls import path
from visualize import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('create-key', views.KeyCreateView.as_view()),
    path('show-keys', views.KeyShowView.as_view()),
    path('delete-key', views.KeyDeleteView.as_view()),
    path('view', views.VisualizeView.as_view()),
]