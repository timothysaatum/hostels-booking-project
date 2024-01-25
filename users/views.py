from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Complain, Contact
#from .models import RoomUser
from django.urls import reverse_lazy
#from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from atlass.utils import send_email_with_transaction
from django.contrib.auth.mixins import LoginRequiredMixin







user = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f'Accounted created for {first_name} {last_name}')
            subject = 'Welcome to unarcom - Your Gateway to Memorable Stays!'
            body = f'''
            Dear {last_name},
            Welcome aboard to unarcom! We're absolutely thrilled to have you join
            our community.

            At unarcom, we're dedicated to making your student life experiences unforgettable.
            Whether you're looking for a luxurious hostel or something to fit your budget,
            we've got you covered. With a vast selection of hostels nation wide,
            you can explore, book, and enjoy hassle-free stays in the most remarkable destinations.

            Here's what you can look forward to as a member of our community:

            1. Endless Possibilities: Discover a vast array of hostels and accommodation, from workers to students,
            ensuring that there's something for every traveler and budget.

            2. Personalized Recommendations: We'll provide you with tailored hotel suggestions based on your preferences
            and past bookings, making your search for the perfect stay a breeze.

            3. Exclusive Offers: As a valued member, you'll gain access to special discounts, deals, and promotions that will
            help you make the most of your travel budget.

            4. Easy Booking: Our user-friendly platform allows you to browse, compare, and book your ideal accommodations with just a few clicks.

            5. 24/7 Customer Support: Our dedicated support team is here to assist you around the clock, ensuring a smooth and stress-free booking experience.

            To get started, simply log in to your account on https://www.trustunarcom.com/users/login/, start exploring our diverse
            range of accommodations, and book your next adventure with confidence.

            We're here to make every journey you embark on a memorable one. Thank you for choosing unarcom, and we can't wait to help you
            create lasting memories.

            If you have any questions or need assistance with anything,
            please don't hesitate to reach out to our friendly customer support team at timothysaatum@gmail.com.

            Happy travels, and welcome to the unarcom family!

            Warm regards,

            The Unarcom Team
            https://www.trustunarcom.com/
            Email: timothysaatum@gmail.com
            Phone: 0594438287
            '''
            recipient_list = [form.cleaned_data['email']]
            send_email_with_transaction(subject, body, recipient_list)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})


@login_required
def profile(request):
    #user = RoomUser.objects.filter(id=request.user.id)
    return render(request, 'users/profile.html')


class ComplainView(CreateView):
    model = Complain
    fields = ('subject', 'message')
    template_name = 'users/complains.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.email = self.request.user.email
        form.instance.phone = self.request.user.telephone
        form.instance.full_name = self.request.user.first_name + ' ' + self.request.user.last_name
        messages.success = 'Data successfully submitted. We will attend to you shortly.'
        return super().form_valid(form)



class ContactView(LoginRequiredMixin, CreateView):
    model = Contact
    fields = ('subject', 'message')
    template_name = 'users/contact.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.email = self.request.user.email
        form.instance.phone = self.request.user.telephone
        form.instance.full_name = self.request.user.first_name + ' ' + self.request.user.last_name
        messages.success = 'Data successfully submitted. We will attend to you shortly.'
        return super().form_valid(form)



class DataHandlingView(TemplateView):
    template_name = 'users/datahandling.html'



class TermsAndConditions(TemplateView):
    template_name = 'users/terms_and_conditions.html'



class PrivacyPolicy(TemplateView):
    template_name = 'users/privacy.html'

class FAQs(TemplateView):
    template_name = 'users/faqs.html'