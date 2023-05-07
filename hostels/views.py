from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Hostel, Booking
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import PayForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core import serializers
# from atlas.transaction import initiate_payment


user = get_user_model()


def home(request):
    students_hostels = Hostel.objects.all()[0:12]
    #apartments = Apartment.objects.all()[0:8]
    return render(request, 'hostels/index.html', {'hostels':students_hostels})


@method_decorator(csrf_exempt, name='dispatch')
class RoomsListView(ListView):
    model = Hostel
    context_object_name = 'hostels'
    template_name = 'hostels/rooms.html'
    slug_url_kwarg = 'pk'
    ordering = ['-date_added']


    def get_queryset(self):
        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            school = self.request.GET.get('query')
            print(school)
            hosts = Hostel.objects.filter(school__name__icontains=school)
            #hostels = serializers.serialize('json', hostels)
            print(hosts)
            return hosts
        else:
            hostels = Hostel.objects.all()
            return hostels

    #def get_template_names(self):
    #    if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
    #        return ['hostels/rooms.html']
    #    else:
    #        return [self.template_name]



class HostelDetailView(DetailView):
    model = Hostel


def services(request):
    return render(request, 'hostels/services.html')


def mission(request):
    return render(request, 'hostels/mission.html')


def howitworks(request):
    return render(request, 'hostels/howitworks.html')


def about(request):
    count = Hostel.objects.all().count()
    all_users = get_user_model().objects.all().count()
    return render(request, 'hostels/about.html', {'count': count, 'all_users': all_users})


def contact(request):
    return render(request, 'hostels/contact.html')


@login_required
def food(request):
    # rests = Restaurant.objects.all()
    return render(request, 'hostels/food.html')

@login_required
def make_booking(request, pk):
    hostel = Hostel.objects.get(pk=pk)
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            momo_no = form.cleaned_data['momo_no']
            account_no = form.cleaned_data['account_no']
            message = form.cleaned_data['message']
            Booking.objects.create(hostel=hostel, tenant=request.user, momo_no=momo_no, cost=hostel.get_cost(
            ), room_no=pk, account_no=account_no, message=message)
            # initiate_payment(amount=hostel.cost_per_room, account_number=momo_no)
        return redirect('booking-details')

    form = PayForm()

    return render(request, 'hostels/booking_form.html', {'form': form})


def dashboard(request):
    dash = Booking.objects.filter(tenant=request.user)
    return render(request, 'hostels/dashboard.html', {'dash':dash})