from django.shortcuts import render
from .models import Booking, LeaveRequests
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView, CreateView
from .forms import RequestToLeaveForm




class DeleteBooking(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('booking-details')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(tenant=self.request.user)



class RequestToLeave(LoginRequiredMixin, CreateView):
    model = LeaveRequests
    template_name = 'atlass/leaverequests_form.html'
    form_class = RequestToLeaveForm
    success_url = reverse_lazy('rooms')

    def form_valid(self, form):
        booking = Booking.objects.filter(tenant=self.request.user).first()
        spec_hostel = booking.room_type.hostel
        room = booking.room
        form.instance.hostel = spec_hostel
        form.instance.room = room
        return super().form_valid(form)