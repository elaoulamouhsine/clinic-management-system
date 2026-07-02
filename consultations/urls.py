from django.urls import path
from . import views

urlpatterns = [
    path('nouvelle/<int:rdv_id>/', views.ConsultationCreateView.as_view(), name='creer_consultation'),
]