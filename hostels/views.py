from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Hostel, Booking
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import PayForm
#from atlas.transaction import initiate_payment


user = get_user_model()


def home(request):
    return render(request, 'hostels/index.html')


class HostelListView(ListView):
    model = Hostel
    context_object_name = 'hostels'
    template_name = 'hostels/rooms.html'
    slug_url_kwarg = 'pk'
    ordering = ['-date_added']


class HostelDetailView(DetailView):
    model = Hostel


def category_500_1000(request):
    category_500_1000 = Hostel.objects.filter(category=1)
    return render(request, 'hostels/category_500_1000.html',
                  {'category_500_1000': category_500_1000})


def category_1100_1500(request):
    category_1100_1500 = Hostel.objects.filter(category=2)
    return render(request, 'hostels/category_1100_1500.html',
                  {'category_1100_1500': category_1100_1500})


def category_1600_2000(request):
    category_1600_2000 = Hostel.objects.filter(category=3)
    return render(request, 'hostels/category_1600_2000.html',
                  {'category_1600_2000': category_1600_2000})


def about(request):
    count = Hostel.objects.all().count()
    all_users= get_user_model().objects.all().count()
    return render(request, 'hostels/about.html', {'count':count, 'all_users':all_users})


def contact(request):
    return render(request, 'hostels/contact.html')

@login_required
def food(request):
    #rests = Restaurant.objects.all()
    return render(request, 'hostels/food.html')



def make_booking(request, pk):
    hostel = Hostel.objects.get(pk=pk)
    if request.method == 'POST':
        form = PayForm(request.POST)
        if form.is_valid():
            momo_no = form.cleaned_data['momo_no']
            account_no = form.cleaned_data['account_no']
            message = form.cleaned_data['message']
            Booking.objects.create(hostel=hostel, tenant=request.user, momo_no=momo_no
                , cost=hostel.get_cost(), room_no=pk, account_no=account_no, message=message)
            #initiate_payment(amount=hostel.cost_per_room, account_number=momo_no)
        return redirect('rooms')

    form = PayForm()

    return render(request, 'hostels/booking_form.html', {'form':form})


class BookingDetailView(DetailView):
    model = Booking
    context_object_name = 'details'
