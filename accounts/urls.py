from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    DispatchDashboardView, 
    DoctorDashboardView, 
    SecretaryDashboardView, 
    PatientDashboardView,
    HomeView,
    AddPatientView,
    PatientHistoryView
)

urlpatterns = [
    # LoginView est déjà une CBV fournie par Django. On précise juste le template.
    path('', HomeView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Nos Vues Personnalisées
    path('dashboard/', DispatchDashboardView.as_view(), name='dispatch_dashboard'),
    path('medecin/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('secretaire/', SecretaryDashboardView.as_view(), name='secretary_dashboard'),
    path('patient/ajouter/', AddPatientView.as_view(), name='add_patient'),
    path('patient/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('patient/historique/', PatientHistoryView.as_view(), name='patient_history'),
]