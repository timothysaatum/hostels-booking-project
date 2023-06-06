from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Hostel, HostelImages
from atlass.models import Booking, Account
from properties.models import Apartment, Property
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import PayForm, CreateHostelForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core import serializers
import smtplib
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


user = get_user_model()


def home(request):

    students_hostels = Hostel.objects.all().order_by('-date_added')[0:12]
    apartments = Apartment.objects.all().order_by('-created_at')[0:12]
    general_properties = Property.objects.all().order_by('-date_added')[0:12]

    return render(request, 'hostels/index.html', {'hostels':students_hostels, 'apartments':apartments, 
        'general_properties':general_properties})


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
            print(hosts)
            return hosts

        else:
            hostels = Hostel.objects.all().order_by('-date_added')
            return hostels




class HostelDetailView(DetailView):

    model = Hostel

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        context = super(HostelDetailView, self).get_context_data(**kwargs)
        context['image_list'] = HostelImages.objects.filter(hostel_id=pk)            
        return context



class Services(TemplateView):
    template_name = 'hostels/services.html'



class Mission(TemplateView):
    template_name = 'hostels/mission.html'



class HowItWorks(TemplateView):
    template_name = 'hostels/howitworks.html'



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

            phone_number = form.cleaned_data['phone_number']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_address = form.cleaned_data['email_address']
            city_or_town = form.cleaned_data['city_or_town']
            university_identification_number = form.cleaned_data['university_identification_number']
            region_of_residence = form.cleaned_data['region_of_residence']
            digital_address = form.cleaned_data['digital_address']

            hostel = Hostel.objects.get(pk=pk)
            rooms = hostel.no_of_rooms

            #booking = Booking.objects.filter()
            booking = Booking.objects.create(hostel=hostel, tenant=request.user, phone_number=phone_number, 
                cost=hostel.get_cost(
            ), room_no=3, first_name=first_name, last_name=last_name, 
                email_address=email_address, city_or_town=city_or_town, 
            university_identification_number=university_identification_number, 
            region_of_residence=region_of_residence, 
            digital_address=digital_address)

            booking.save()

            #create an account for the user when they make a booking
            acc = Account.objects.filter(user_id=request.user.id)
            #checking to see if user already have an account
            if not acc:
                Account.objects.create(user_id=request.user.id, booking_for_id=pk)

            #sending email to the user
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
            key = settings.PAYSTACK_PUBLIC_KEY
            context = {
                'booking':booking,
                'field_values':request.POST,
                'paystack_pub_key':key,
                'amount_value':booking.amount_value(),
            }

            #return render(request, 'hostels/make_payment.html', context)

            return redirect('booking-details')

        #return redirect('booking-details')

    form = PayForm()

    return render(request, 'hostels/booking_form.html', {'form': form})

def verify_booking(request, ref):
    booking = Booking.objects.get(ref=ref)
    verified = booking.verify_payment

    if verified:
        account = Account.objects.get(user=request.user)
        account.balance += booking.cost
        account.save()
        return render(request, 'hostels/payment_success.html')
    return render(request, 'hostels/payment_success.html')

class CreateHostel(LoginRequiredMixin, CreateView):

    model = Hostel
    form_class = CreateHostelForm
    success_url = '/hostel/create/'
    template_name = 'hostels/create.html'

    def form_valid(self, form):
        form.instance.hostel_amenities = dict(item.split('=') for item in form.cleaned_data['amenities'].split(','))
        form.instance.user_name = self.request.user
        return super().form_valid(form)


@login_required
def dashboard(request):

    dash = Booking.objects.filter(tenant=request.user)

    return render(request, 'hostels/dashboard.html', {'dash':dash})

@login_required
def hostel_manager(request):
    return render(request, 'hostels/management.html')

@login_required
def tenants(request):
    tenants = Booking.objects.filter(id=request.user.id)
    print(tenants)
    return render(request, 'hostels/tenants.html', {'tenants':tenants})
