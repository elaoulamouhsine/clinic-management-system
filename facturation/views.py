from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Facture


class FactureListView(LoginRequiredMixin, ListView):
    model = Facture
    template_name = 'facturation/liste_factures.html'
    context_object_name = 'factures'

    def get_queryset(self):
        queryset = Facture.objects.select_related(
            'consultation__rdv__patient__user',
            'consultation__rdv__docteur__user'
        ).all()

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(consultation__rdv__patient__user__last_name__icontains=q) |
                Q(consultation__rdv__patient__user__first_name__icontains=q)
            )

        return queryset.order_by('statut_paiement', '-date_facture')


class PayerFactureView(LoginRequiredMixin, View):
    """ Action rapide pour marquer une facture comme payée """
    def post(self, request, pk):
        facture = get_object_or_404(Facture, pk=pk)
        if facture.statut_paiement != 'PAYE':
            facture.statut_paiement = 'PAYE'
            facture.save()
            messages.success(request, f"La facture #{facture.id} a été marquée comme PAYÉE.")
        return redirect('liste_factures')
