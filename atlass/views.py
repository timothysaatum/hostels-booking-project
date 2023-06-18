from django.shortcuts import render
from .models import Booking
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView



class DeleteBooking(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('delete-booking', 'pk')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)