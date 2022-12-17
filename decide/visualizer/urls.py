from django.urls import path
from . import views


urlpatterns = [
    path('<int:voting_id>/', views.get_context_data),
]
