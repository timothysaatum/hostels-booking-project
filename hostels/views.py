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
import smtplib
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
#from atlass.transaction import initiate_payment


user = get_user_model()


def home(request):

    students_hostels = Hostel.objects.all().order_by('-date_added')[0:12]
    #apartments = Apartment.objects.all()[0:8]

    return render(request, 'hostels/index.html', {'hostels':students_hostels})


@method_decorator(csrf_exempt, name='dispatch')
class RoomsListView(ListView):

    model = Hostel
    context_object_name = 'hostels'
    template_name = 'hostels/rooms.html'
    slug_url_kwarg = 'pk'


    def get_queryset(self):

        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':

            school = self.request.GET.get('query')
            print(school)
            hosts = Hostel.objects.filter(school__name__icontains=school).order_by('-date_added')
            #hostels = serializers.serialize('json', hostels)
            print(hosts)
            return hosts

        else:
            hostels = Hostel.objects.all().order_by('-date_added')
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



@login_required
def make_booking(request, pk):

    ROOM_NO = 1

    if request.method == 'POST':

        form = PayForm(request.POST)

        if form.is_valid():

            momo_no = form.cleaned_data['momo_no']
            message = form.cleaned_data['message']

            hostel = Hostel.objects.get(pk=pk)
            rooms = hostel.no_of_rooms

            try:
                booking_is_available = Booking.objects.exists()
            except ObjectDoesNotExist:
                booking_is_available = None

            if booking_is_available:

                latest_room_no = booking_is_available.latest('room_no')

            else:
                pass

            if latest_room_no != rooms:
                ROOM_NO = latest_room_no + 1

            elif latest_room_no ==  rooms:
                ROOM_NO = rooms
            else:
                ROOM_NO

            Booking.objects.create(hostel=hostel, tenant=request.user, mobile_money_number=momo_no, cost=hostel.get_cost(
            ), room_no=ROOM_NO, message=message)


            #with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            #    smtp.ehlo()
            #    smtp.starttls()
            #    smtp.ehlo()
            #    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            #    subj = 'hi from gods'
            #    body = 'it is well'
            #
            #    msg = f'Subject: {subj}\n\n{body}'
            #
            #    smtp.sendmail(settings.EMAIL_HOST_USER, 'saatumtimothy@gmail.com', msg)
        return redirect('booking-details')

    form = PayForm()

    return render(request, 'hostels/booking_form.html', {'form': form})

@login_required
def dashboard(request):

    dash = Booking.objects.filter(tenant=request.user)

    return render(request, 'hostels/dashboard.html', {'dash':dash})