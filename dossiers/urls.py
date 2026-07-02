from django.urls import path
from .views import PatientListView

urlpatterns = [
    path('patients/', PatientListView.as_view(), name='liste_patients'),
]