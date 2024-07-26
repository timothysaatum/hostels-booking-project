from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView, DeleteView, UpdateView, View
from .models import Hostel, RoomType, RoomTypeImages, Room, Amenities
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
from .distance import find_ip_address





user = get_user_model()


class HomeView(ListView):

    model = Hostel

    template_name = 'hostels/index.html'

    context_object_name = 'hostels'

    slug_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):

        context = super(HomeView, self).get_context_data(**kwargs)

        context['hostels'] = context['hostels'][0:12]

        #context['apartments'] = Apartment.objects.all()[0:12]

        #context['general_properties'] = Property.objects.all()[0:12]

        ip = find_ip_address(self.request)

        print(f'Your IP is: {ip}')

        return context





@method_decorator(csrf_exempt, name='dispatch')
class HostelsListView(ListView):

    model = Hostel

    context_object_name = 'hostels'

    template_name = 'hostels/hostel_list.html'

    slug_url_kwarg = 'pk'



class RoomsListView(ListView):

    model = RoomType

    context_object_name = 'rooms'

    template_name = 'hostels/room_list.html'

    slug_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):

        context = super(RoomsListView, self).get_context_data(**kwargs)

        context['room_type_list'] = RoomType.objects.filter(hostel_id=self.kwargs.get('pk'))

        return context


class HostelDetailView(DetailView):

    model = Hostel

    slug_url_kwarg = 'pk'

    context_object_name = 'hostel'

    template_name = 'hostels/room_detail.html'

    def get_context_data(self, **kwargs):

        context = super(HostelDetailView, self).get_context_data(**kwargs)

        hostel_id = self.kwargs.get('pk')

        amenties = Amenities.objects.all()
        #print(amenties)

        context['rooms'] =  RoomType.objects.filter(hostel_id=hostel_id)

        context['image_list'] = RoomTypeImages.objects.filter(room__hostel_id=hostel_id)

        context['front_display'] = RoomTypeImages.objects.filter(room__hostel_id=hostel_id)[0:1]

        context['spec_room'] = Room.objects.select_related('room_type').filter(room_type__hostel_id=hostel_id)
        #print(context['hostel'].amenities.all())
        return context

"""
class RoomDetailView(DetailView):

    model = RoomType
    slug_url_kwarg = 'pk'
    context_object_name = 'room'

    #template_name = 'hostels/room_detail.html'
    def get_context_data(self, **kwargs):

        context = super(RoomDetailView, self).get_context_data(**kwargs)
        context['image_list'] = RoomTypeImages.objects.filter(room_id=self.kwargs.get('pk'))
        context['front_display'] = RoomTypeImages.objects.filter(room_id=self.kwargs.get('pk'))[0:4]
        context['spec_room'] = Room.objects.select_related('room_type').filter(room_type=self.kwargs.get('pk'))     
        return context

"""

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

            number_of_guests = form.cleaned_data['number_of_guests']

            check_in = form.cleaned_data['check_in']

            receipt = str(random.randrange(0, 100)) + university_identification_number

            room = Room.objects.get(pk=room_pk)

            cost = room.room_type.cost_per_head * number_of_guests

            bk = Booking.objects.filter(room_no=room.room_number).first()
            print(bk)
            if bk:

                if (room.room_type == bk.room_type) and (bk.gender != gender):

                    messages.error(request, f'A {gender} cannot book this room because it has a {bk.gender} occupant')
                    
                    return redirect('hostel-details', pk, room.room_type)

                if room.capacity == 0:

                    messages.error(request, f'({room.room_type}) cannot accept extra booking')
                    
                    return redirect('hostel-details', pk, room.room_type)

            if number_of_guests > room.capacity:

                messages.error(request, f'{number_of_guests} cannot book this room because is {room.room_type}')
                    
                return redirect('hostel-details', pk, room.room_type)


            try:
                booking = Booking.objects.create(room=room, tenant=request.user,
                    phone_number=phone_number, room_type=room.room_type,check_in=check_in,
                    cost=cost, number_of_guests=number_of_guests,
                    room_no=room.room_number, first_name=first_name, last_name=last_name, 
                    email_address=email_address,gender=gender, city_or_town=city_or_town, 
                    university_identification_number=university_identification_number, 
                    region_of_residence=region_of_residence, digital_address=digital_address,
                    receipt_number=receipt
                )

            except Exception as e:

                messages.error(request, f'{e}, contact support if the issue persists.')

                return redirect('hostel-details', pk, room.room_type)

            
            #create an account for the user when they make a booking
            acc = Account.objects.filter(user_id=request.user.id)
            
            #checking to see if user already have an account
            if not acc:
                Account.objects.create(user_id=request.user.id, hostel_id=booking.room_type.hostel.pk)

            return redirect('book', booking.pk)
    room = Room.objects.get(pk=room_pk)
    
    form = BookingCreationForm()

    return render(request, 'hostels/booking_form.html', {'form': form, 'room':room})


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

        #Get the account number for the hostel the user is booking
        account_number = booking.get_account_number()
        account_name = booking.account_name()

        #transfering landlord's money after verifying payment
        hostel_fee = booking.cost
        print(hostel_fee)
        account_number = account_number

        hostel_fee = float(hostel_fee)


        #calculating how much should be transferred to the landlord base on
        #our commission rate of 4%
        #this will be uncommented if we agreed a percentage later
        #amount = (hostel_fee / 1.04) * 100
        amount = hostel_fee * 100

        hostel = booking.room_type.hostel
        
        #call transfer to take place
        try:
            xerxes = Xerxes(amount=amount, account_number=account_number, account_name=account_name, hostel=hostel)


            #transferring landlords money
            xerxes.create_recipient()

            xerxes.initiate_transfer()

            xerxes.finalize_transfer()

            xerxes.verify_transfer()

        except Exception as e:

            messages.error(request, f'{e}, Instant cash transfer could not be initiated. Manually verification initiated.')
        
        finally:

            #notify the user of the successful booking
            recipient_list = [booking.email_address]
        
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
            We are dedicated to giving you the best of treatment on campus.
            We are excited to know you believe and trust in us to manage your accomodation proceedings
            on campus.
            Your hostel will be transfered to your landlord. Your room is now secured.
            Find attach your receipt www.trustunarcom.com/booking/receipts/download/
            Do not hesitate to reach out to us with your concerns, our team will respond immediately.
            \n
            Contact us when you are reporting.
            Tel: 0594438287
            Email: timothysaatum@gmail.com
            WhatsApp: 0594438287
            '''

            send_email_with_transaction(subject, body, recipient_list)

        messages.success(request, f'Your booking was successfully verified. Thank you')  

        return redirect('home')

    messages.error(request, f'Your booking could not be verified. You may have to re-book.')

    return redirect('home')


class CreateHostel(LoginRequiredMixin, CreateView):

    model = Hostel

    form_class = HostelCreationForm

    success_url = reverse_lazy('room-create')

    template_name = 'hostels/create.html'

    def form_valid(self, form):

        try:
            
            form.instance.created_by = self.request.user

        except Exception as e:

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
        rel_host = Hostel.objects.filter(created_by=self.request.user).first()
        form.instance.db_use_only = form.cleaned_data['room_type_number']

        form.instance.max_capacity = form.cleaned_data['room_capacity']

        form.instance.room_numbers = room_dict

        form.instance.hostel = rel_host
        form.instance.cost_per_head = float(form.cleaned_data['cost_per_head']) + float(50)#(float(form.cleaned_data['cost_per_head']) * 0.04)

        return super().form_valid(form)



class HostelDelete(LoginRequiredMixin, DeleteView):

    model = Hostel

    success_url = reverse_lazy('management')

    def get_queryset(self):

        queryset = super().get_queryset()

        return queryset.filter(created_by=self.request.user)


class HostelUpdate(LoginRequiredMixin, UpdateView):

    model = Hostel

    template_name = 'hostels/update.html'

    fields = ['owner_name', 'school', 'campus', 'hostel_name', 'contact', 'display_image', 'no_of_rooms',
                'hostel_coordinates', 'cost_range', 'duration_of_rent', 'wifi', 'amenities']


    def get_queryset(self):

        queryset = super().get_queryset()

        return queryset.filter(created_by=self.request.user)


    def get_success_url(self):

        return reverse('hostel-details', kwargs={'pk': self.object.pk, 'hostel':self.object.hostel_name})


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
        
        context['hostels'] = Hostel.objects.filter(created_by=self.request.user)
        
        return context




class VacantRooms(LoginRequiredMixin, ListView):

    model = Room

    template_name = 'hostels/vacant_rooms.html'

    context_object_name = 'rooms'

    def get_context_data(self, **kwargs):

        context = super(VacantRooms, self).get_context_data(**kwargs)

        context['rooms'] = Room.objects.filter(room_type__hostel__created_by=self.request.user).filter(is_full=False)
        
        return context



class BookingsView(LoginRequiredMixin, ListView):

    model = Booking
    
    context_object_name = 'bookings'
    
    template_name = 'hostels/bookings.html'

    def get_context_data(self, **kwargs):
        
        context = super(BookingsView, self).get_context_data(**kwargs)
        
        context['bookings'] = Booking.objects.filter(room_type__hostel__created_by=self.request.user)

        return context



class PendingView(LoginRequiredMixin, ListView):

    model = LeaveRequests
    
    context_object_name = 'pendings'

    template_name = 'hostels/pending_approvals.html'

    def get_context_data(self, **kwargs):

        context = super(PendingView, self).get_context_data(**kwargs)

        context['pendings'] = LeaveRequests.objects.filter(room__room_type__hostel__created_by=self.request.user).filter(is_approved=False)
        
        return context



class ApprovalsView(LoginRequiredMixin, ListView):

    model = LeaveRequests

    context_object_name = 'approved_leaves'

    template_name = 'hostels/approved.html'


    def get_context_data(self, **kwargs):

        context = super(ApprovalsView, self).get_context_data(**kwargs)

        context['approved_leaves'] = LeaveRequests.objects.filter(room__room_type__hostel__created_by=self.request.user).filter(is_approved=True)
        
        return context



class SalesStatistics(LoginRequiredMixin, ListView):

    model = Booking

    context_object_name = 'statistics'

    template_name = 'hostels/statistics.html'



class GeneratePdf(LoginRequiredMixin, DetailView):

    model = Booking

    def get(self, *args, **kwargs):
        print(args)
        booking = Booking.objects.filter(tenant=self.request.user).first()

        context = {'booking':booking}
        
        pdf = create_pdf('hostels/receipt.html', context)

        return HttpResponse(pdf, content_type='application/pdf')


#number = '+233594438287'
#from phonenumberrs import geocoder
#from phonenumbers import carrier
#pepnum = phonenumbers.parse(number)
#location = geocoder.description_for_number(pepnum, 'en')
#print(location)
#service_pro = phonenumbers.parse(number)
#service = carrier.name_for_number(service_pro)
#pip install opencage, folium
#import opencage
#from opencage.geocoder import OpenCageGeocode
#go to open cage web
#copy and create a variable call key
#key = api_key
#geocoder = OpenCageGeocode(key)
#query = str(location)
#results = geocoder.geocode(query)
#print(results)
#lat = results[0]['geometry']['lat']
#lng = results[0]['geometry']['lng']
#import folium
#myMap = folium.Map(location=[lat, lng], zoom_start=9)
#folium.marker([lat, lng], popup=location).add_to(myMap)
#myMap.save('myLocation.html')
