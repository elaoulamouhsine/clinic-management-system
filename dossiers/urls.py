from django.urls import path
from .views import PatientListView # Importe la classe

urlpatterns = [
    path('patients/', PatientListView.as_view(), name='liste_patients'),
]