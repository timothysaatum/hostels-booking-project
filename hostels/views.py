from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView, DeleteView, UpdateView, View
from .models import Hostel, RoomType, RoomTypeImages, Room
from atlass.models import Booking, Account, LeaveRequests
from properties.models import Apartment, Property
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import BookingCreationForm, HostelCreationForm, RoomTypeCreationForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core import serializers
from atlass.utils import send_email_with_transaction, create_pdf
from atlass.transaction import Xerxes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import random
from django.contrib import messages
from django.http import HttpResponse





user = get_user_model()


class HomeView(TemplateView):
    template_name = 'hostels/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['hostels'] = Hostel.objects.all()[0:12]
        context['apartments'] = Apartment.objects.all()[0:12]
        context['general_properties'] = Property.objects.all()[0:12]
        return context



@method_decorator(csrf_exempt, name='dispatch')
class HostelsListView(ListView):

    model = Hostel
    context_object_name = 'hostels'
    template_name = 'hostels/hostel_list.html'
    slug_url_kwarg = 'pk'

    def get_queryset(self):

        if self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':

            school = self.request.GET.get('query')
            print(school)
            hostels = Hostel.objects.filter(school__name__icontains=school).order_by('-date_added')
            print(hostels)

        else:
            hostels = Hostel.objects.all().order_by('-date_added')
        
        return hostels


class RoomsListView(ListView):
    model = RoomType
    context_object_name = 'rooms'
    template_name = 'hostels/room_list.html'
    slug_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super(RoomsListView, self).get_context_data(**kwargs)
        context['room_type_list'] = RoomType.objects.filter(hostel_id=self.kwargs.get('pk'))
        return context



class RoomDetailView(DetailView):

    model = RoomType
    slug_url_kwarg = 'pk'
    context_object_name = 'room'

    template_name = 'hostels/room_detail.html'
    def get_context_data(self, **kwargs):

        context = super(RoomDetailView, self).get_context_data(**kwargs)
        context['image_list'] = RoomTypeImages.objects.filter(room_id=self.kwargs.get('pk'))
        context['front_display'] = RoomTypeImages.objects.filter(room_id=self.kwargs.get('pk'))[0:4]
        context['spec_room'] = Room.objects.select_related('room_type').filter(room_type=self.kwargs.get('pk'))     
        return context



class Services(TemplateView):
    template_name = 'hostels/services.html'



class Mission(TemplateView):
    template_name = 'hostels/mission.html'



class HowItWorks(TemplateView):
    template_name = 'hostels/howitworks.html'



class AboutView(TemplateView):
    template_name = 'hostels/about.html'




@login_required
def make_booking(request, pk, room_pk):

    if request.method == 'POST':

        form = BookingCreationForm(request.POST)

        if form.is_valid():

            phone_number = form.cleaned_data['phone_number']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email_address = form.cleaned_data['email_address']
            city_or_town = form.cleaned_data['city_or_town']
            university_identification_number = form.cleaned_data['university_identification_number']
            region_of_residence = form.cleaned_data['region_of_residence']
            digital_address = form.cleaned_data['digital_address']
            gender = form.cleaned_data['gender']
            #check_in = form.cleaned_data['check_in']
            receipt = str(random.randrange(0, 100)) + university_identification_number
            room = Room.objects.get(pk=room_pk)


            #charge_money(room.room_type.cost_per_head, email_address)
            bk = Booking.objects.filter(room_no=room.room_number).first()
            if bk:

                if (room.room_type == bk.room_type) and (bk.gender != gender):

                    messages.error(request, f'A {gender} cannot book this room because it has a {bk.gender} occupant')
                    
                    return redirect('room-detail', pk, room.room_type)

                if room.capacity == 0:

                    messages.error(request, f'({room.room_type}) cannot accept extra booking')

                    return redirect('room-detail', pk, room.room_type)


            
            booking = Booking.objects.create(room=room, tenant=request.user,
                    phone_number=phone_number, room_type=room.room_type,
                    cost=room.room_type.cost_per_head, 
                    room_no=room.room_number, first_name=first_name, last_name=last_name, 
                    email_address=email_address,gender=gender, city_or_town=city_or_town, 
                    university_identification_number=university_identification_number, 
                    region_of_residence=region_of_residence, digital_address=digital_address,
                    receipt_number=receipt
                )

            
            #create an account for the user when they make a booking
            acc = Account.objects.filter(user_id=request.user.id)
            
                #checking to see if user already have an account
            if not acc:
                Account.objects.create(user_id=request.user.id)

            return redirect('book', booking.pk)

    form = BookingCreationForm()

    return render(request, 'hostels/booking_form.html', {'form': form})


@login_required
def make_payment(request, pk):

    booking = Booking.objects.get(pk=pk)
    key = settings.PAYSTACK_PUBLIC_KEY
    
    return render(request, 'hostels/make_payment.html', {'booking':booking, 'paystack_pub_key':key})


@login_required
def verify_booking(request, ref):

    booking = Booking.objects.get(ref=ref)
    verified = booking.verify_payment

    if verified:

        account = Account.objects.get(user=request.user)
        account.balance += booking.cost
        booking.is_verified = True
        booking.save()
        account.save()
        account_number = booking.get_account_number()

        #transfering landlord's money after verifying payment
        hostel_fee = booking.cost
        account_number = '0257446404'

        hostel_fee = float(hostel_fee)

        amount = (hostel_fee / 1.02) * 100

        hostel = booking.room_type.hostel
        
        #call transfer to take place
        xerxes = Xerxes(amount=amount, account_number=account_number, hostel=hostel)


        #transferring landlords money
        xerxes.create_recipient()
        xerxes.initiate_transfer()
        xerxes.finalize_transfer()
        xerxes.verify_transfer()

        #notify the user of the successful booking
        recipient_list = [booking.email_address]
        #recipient_list = ['saatumtimothy@gmail.com']
        #email subject
        subject = 'Thank you for booking with us.'

        #email body
        body = f'''\n
        Thank you for booking with us.
        \n
        Hostel:{booking.get_hostel()}
        Room Type:{booking.room_type} 
        Room No:{booking.room_no}
        Receipt No:{booking.receipt_number}
        \n
        We are dedicated to giving you the best treatment on campus.
        We are excited to know you believe and trust in us to manage your accomodation proceedings
        on campus.
        Your hostel fee has been successfully transfered to your landlord. Your room is now secured.
        Find attach you receipt www.trustunarcom.com/booking/receipts/download/
        Do not hesitate to reach out to us with your concerns, our team will respond immediately.
        \n
        Contact us when you are reporting.
        Tel: 0594438287
        Mail: unarcom@company.com
        WhatsApp: 0594438287
        '''

        #send email function call
        try:
            send_email_with_transaction(subject, body, recipient_list)
        except Exception as e:
            raise e  
        messages.success(request, 'Your booking was successfully verified. Thank you')      
        return redirect('home')
    messages.error(request, 'Your booking could not be verified')
    return redirect('home')


class CreateHostel(LoginRequiredMixin, CreateView):

    model = Hostel
    form_class = HostelCreationForm
    success_url = reverse_lazy('room-create')
    template_name = 'hostels/create.html'

    def form_valid(self, form):
        try:
            form.instance.hostel_amenities = dict(item.split('=') for item in form.cleaned_data['amenities'].split(','))
            form.instance.created_by = self.request.user
        except exception as e:
            raise e

        return super().form_valid(form)



class RoomTypeCreateView(LoginRequiredMixin, CreateView):
    model = RoomType

    form_class = RoomTypeCreationForm
    success_url = reverse_lazy('room-create')

    def form_valid(self, form):
        list_room_numbers = form.cleaned_data['room_numbers'].split(',')
        room_dict = {}

        for val in range(len(list_room_numbers)):

            room_dict_key = 'room' + str(val)
            room_dict.update({room_dict_key:list_room_numbers[val]})
        

        #instantiating room values before saving
        rel_host = Hostel.objects.get(created_by=self.request.user)
        form.instance.db_use_only = form.cleaned_data['room_type_number']
        form.instance.room_numbers = room_dict
        form.instance.hostel = rel_host
        form.instance.cost_per_head = float(form.cleaned_data['cost_per_head']) + (float(form.cleaned_data['cost_per_head']) * 0.02)

        return super().form_valid(form)



class HostelDelete(LoginRequiredMixin, DeleteView):
    model = Hostel
    success_url = reverse_lazy('management')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)


class HostelUpdate(LoginRequiredMixin, DeleteView):
    model = Hostel
    template_name = 'hostels/update.html'
    fields = ['owner_name', 'school', 'campus', 'hostel_name', 'contact', 'display_image', 'no_of_rooms'
                'hostel_coordinates', 'cost_range', 'duration_of_rent', 'wifi', 'hostel_amenities']
    success_url = reverse_lazy('hostel-detail')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)


@login_required
def user_dashboard(request):

    dash = Booking.objects.filter(tenant=request.user)

    return render(request, 'hostels/user_dashboard.html', {'dash':dash})


class Management(LoginRequiredMixin, ListView):

    model = Booking
    slug_url_kwarg = 'pk'
    context_object_name = 'bookings'
    template_name = 'hostels/management.html'

    def get_context_data(self, **kwargs):
        context = super(Management, self).get_context_data(**kwargs)
        context['bookings'] = Booking.objects.filter(room_type__hostel__created_by=self.request.user)
        context['vacancies'] = Room.objects.filter(room_type__hostel__created_by=self.request.user).filter(is_full=False)
        context['approved_leaves'] = LeaveRequests.objects.filter(room__room_type__hostel__created_by=self.request.user).filter(is_approved=True)
        context['pending_approvals'] = LeaveRequests.objects.filter(room__room_type__hostel__created_by=self.request.user).filter(is_approved=False)
        return context


class GeneratePdf(LoginRequiredMixin, DetailView):
    model = Booking
    def get(self, *args, **kwargs):
        booking = Booking.objects.filter(tenant=self.request.user).first()
        context = {'booking':booking}
        pdf = create_pdf('hostels/receipt.html', context)

        return HttpResponse(pdf, content_type='application/pdf')
