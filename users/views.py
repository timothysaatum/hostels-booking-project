from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required




def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            last_name = form.cleaned_data.get('last_name')
            messages.success(request, f'Accounted created for {last_name}')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')
