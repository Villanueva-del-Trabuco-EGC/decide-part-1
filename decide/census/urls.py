from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('manage', views.CensusView.as_view(), name='census_manage'),
    path('export/<int:voting_id>/', views.export_census, name='export'),
]
