from django.urls import path
from . import views

urlpatterns = [
   path('nouveau/', views.RequestRDVView.as_view(), name='request_rdv'),
   path('liste/', views.RDVListView.as_view(), name='liste_rendez_vous'),
   # Modifier (prend un ID int:pk)
    path('modifier/<int:pk>/', views.RDVUpdateView.as_view(), name='modifier_rdv'),
    # Changer Statut (prend un ID et le code du statut 'CONFIRME' ou 'ANNULE')
    path('statut/<int:pk>/<str:statut_code>/', views.RDVStatutView.as_view(), name='changer_statut_rdv'),
]
 