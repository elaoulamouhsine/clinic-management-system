from django.urls import path
from . import views

urlpatterns = [
    # L'URL prend l'ID du RDV comme paramètre
    path('nouvelle/<int:rdv_id>/', views.ConsultationCreateView.as_view(), name='creer_consultation'),
]