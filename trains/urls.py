from django.urls import path

from .views import TrainDetailView, TrainListCreateView, TrainSearchView

urlpatterns = [
    path("", TrainListCreateView.as_view(), name="train-create"),
    path("search/", TrainSearchView.as_view(), name="train-search"),
    path("<int:pk>/", TrainDetailView.as_view(), name="train-detail"),
]
