from django.urls import path
from . import views

urlpatterns = [
    path('liste/', views.FactureListView.as_view(), name='liste_factures'),
    path('payer/<int:pk>/', views.PayerFactureView.as_view(), name='payer_facture'),
]