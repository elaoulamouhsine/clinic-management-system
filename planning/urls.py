from django.urls import path
from . import views

urlpatterns = [
   path('nouveau/', views.RequestRDVView.as_view(), name='request_rdv'),
   path('liste/', views.RDVListView.as_view(), name='liste_rendez_vous'),
]
 