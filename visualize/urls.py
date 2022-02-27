from django.urls import path
from visualize import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('create-key', views.KeyCreateView.as_view()), # /create-key
    path('show-keys', views.KeyShowView.as_view()), # /show-keys
    path('delete-key', views.KeyDeleteView.as_view()), # /delete-key
    path('view', views.VisualizeEntranceView.as_view()), # /view
    path('time-series', views.VisualizeTimeSeriesView.as_view()), # /time-series
    path('intraday', views.VisualizeIntradayView.as_view()), # /intraday
    path('refresh-authorization-key', views.VisualizeAuthorizationKeyRefreshView.as_view()), # /refresh-authorization-key
]