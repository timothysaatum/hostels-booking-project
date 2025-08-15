from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .models import Complain, Contact
from .models import RoomUser
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from atlass.utils import send_email_with_transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views






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
            We are always available to serve you. Customer satisfaction has always been our hallmark. 
            Let's strive to help each other
            #You deserve the best.
             '''
            recipient_list = [form.cleaned_data['email']]
            #send_email_with_transaction(subject, body, recipient_list)
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
    success_url = reverse_lazy('hostels:home')

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
    success_url = reverse_lazy('hostels:home')

    def form_valid(self, form):
        form.instance.email = self.request.user.email
        form.instance.phone = self.request.user.telephone
        form.instance.full_name = self.request.user.first_name + ' ' + self.request.user.last_name
        messages.success = 'Data successfully submitted. We will attend to you shortly.'
        return super().form_valid(form)


def login_redirect(request):
    if request.user.has_a_hostel:
        return redirect('hostels:home')
    else:
        return redirect('hostels:home')


class DataHandlingView(TemplateView):
    template_name = 'users/datahandling.html'



class TermsAndConditions(TemplateView):
    template_name = 'users/terms_and_conditions.html'



class PrivacyPolicy(TemplateView):
    template_name = 'users/privacy.html'

class FAQs(TemplateView):
    template_name = 'users/faqs.html'