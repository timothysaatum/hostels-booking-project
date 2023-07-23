from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Complain, Contact
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from atlass.utils import send_email_with_transaction







user = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            last_name = form.cleaned_data.get('last_name')
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f'Accounted created for {first_name} {last_name}')
            subject = 'Welcome to the UNARCOM world'
            body = f'''
            Hi {last_name}, thank you for registering a rewarding account with us. Find the best of what you need.
             \nWe are always available to serve you. Customer satisfaction has always been our hallmark.
             Let's strive to help each other
             #You deserve the best.
             '''
            recipient_list = ['saatumtimothy@gmail.com']
            send_email_with_transaction(subject, body, recipient_list)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})


@login_required
def profile(request):
    #user = RoomUser.objects.filter(id=request.user.id)
    return render(request, 'users/profile.html')


class ComplainView(CreateView):
    model = Complain
    fields = ('email', 'phone', 'address', 'full_name', 'message')
    template_name = 'users/complains.html'


class ContactView(CreateView):
    model = Contact
    fields = ('email', 'phone', 'address', 'full_name', 'message')
    template_name = 'users/contact.html'
    success_url = reverse_lazy('/')


class DataHandlingView(TemplateView):
    template_name = 'users/datahandling.html'

class TermsAndConditions(TemplateView):
    template_name = 'users/terms_and_conditions.html'


class PrivacyPolicy(TemplateView):
    template_name = 'users/privacy.html'

class FAQs(TemplateView):
    template_name = 'users/faqs.html'