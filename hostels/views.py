# from django.shortcuts import render, get_object_or_404, redirect
# from django.views.generic import (
#     ListView, DetailView, CreateView, UpdateView, DeleteView
# )
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.contrib import messages
# from django.urls import reverse_lazy, reverse
# from django.db.models import Q, Prefetch
# from django.core.paginator import Paginator
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# from django.db import transaction

# from .models import Hostel, RoomType, School, Amenity, HostelImage, RoomTypeImage, ContactInquiry
# from .forms import (
#     HostelCreateForm, HostelUpdateForm, RoomTypeForm, 
#     ContactInquiryForm, HostelImageFormSet, RoomTypeImageFormSet
# )


# class HostelListView(ListView):
#     """Public view for students to browse hostels"""
#     model = Hostel
#     template_name = 'hostels/hostel_list.html'
#     context_object_name = 'hostels'
#     paginate_by = 12

#     def get_queryset(self):
#         queryset = Hostel.active.all().with_stats()
        
#         # Search functionality
#         search_query = self.request.GET.get('search')
#         if search_query:
#             queryset = queryset.search(search_query)
        
#         # Filter by school
#         school_id = self.request.GET.get('school')
#         if school_id:
#             queryset = queryset.filter(school_id=school_id)
        
#         # Filter by price range
#         min_price = self.request.GET.get('min_price')
#         max_price = self.request.GET.get('max_price')
#         if min_price:
#             queryset = queryset.filter(min_price__gte=min_price)
#         if max_price:
#             queryset = queryset.filter(max_price__lte=max_price)
        
#         # Filter by amenities
#         amenities = self.request.GET.getlist('amenities')
#         if amenities:
#             queryset = queryset.filter(amenities__in=amenities).distinct()
        
#         # Filter by wifi
#         has_wifi = self.request.GET.get('has_wifi')
#         if has_wifi == 'true':
#             queryset = queryset.filter(has_wifi=True)
        
#         # Sorting
#         sort_by = self.request.GET.get('sort', '-is_featured')
#         if sort_by == 'price_low':
#             queryset = queryset.order_by('min_price')
#         elif sort_by == 'price_high':
#             queryset = queryset.order_by('-min_price')
#         elif sort_by == 'rating':
#             queryset = queryset.order_by('-rating')
#         elif sort_by == 'newest':
#             queryset = queryset.order_by('-created_at')
#         else:
#             queryset = queryset.order_by('-is_featured', '-created_at')
        
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['schools'] = School.active.all()
#         context['amenities'] = Amenity.active.all()
        
#         # Preserve filters in context
#         context['current_search'] = self.request.GET.get('search', '')
#         context['current_school'] = self.request.GET.get('school', '')
#         context['current_min_price'] = self.request.GET.get('min_price', '')
#         context['current_max_price'] = self.request.GET.get('max_price', '')
#         context['current_amenities'] = self.request.GET.getlist('amenities')
#         context['current_wifi'] = self.request.GET.get('has_wifi', '')
#         context['current_sort'] = self.request.GET.get('sort', '-is_featured')
        
#         return context


# class HostelDetailView(DetailView):
#     """Detailed view of a hostel for students"""
#     model = Hostel
#     template_name = 'hostels/hostel_detail.html'
#     context_object_name = 'hostel'
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'

#     def get_queryset(self):
#         return Hostel.active.all().select_related('school', 'owner').prefetch_related(
#             'amenities',
#             'images',
#             Prefetch('room_types', queryset=RoomType.objects.prefetch_related('images'))
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['contact_form'] = ContactInquiryForm()
#         context['similar_hostels'] = Hostel.active.all().filter(
#             school=self.object.school
#         ).exclude(id=self.object.id)[:4]
#         return context


# class HostelCreateView(LoginRequiredMixin, CreateView):
#     """Create new hostel - for authenticated users"""
#     model = Hostel
#     form_class = HostelCreateForm
#     template_name = 'hostels/hostel_form.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.POST:
#             context['image_formset'] = HostelImageFormSet(self.request.POST, self.request.FILES)
#         else:
#             context['image_formset'] = HostelImageFormSet()
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         image_formset = context['image_formset']
        
#         with transaction.atomic():
#             form.instance.owner = self.request.user
#             form.instance.owner_name = self.request.user.full_name or self.request.user.email
#             self.object = form.save()
            
#             if image_formset.is_valid():
#                 image_formset.instance = self.object
#                 image_formset.save()
        
#         messages.success(self.request, 'Hostel created successfully! Now add your room types.')
#         return super().form_valid(form)

#     def get_success_url(self):
#         # Redirect to room type creation with a flag to indicate it's a new hostel
#         return reverse('hostels:roomtype-create', kwargs={'hostel_slug': self.object.slug}) + '?new_hostel=1'


# class HostelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     """Update hostel - only for hostel owner"""
#     model = Hostel
#     form_class = HostelUpdateForm
#     template_name = 'hostels/hostel_update.html'
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'

#     def test_func(self):
#         return self.get_object().owner == self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.POST:
#             context['image_formset'] = HostelImageFormSet(
#                 self.request.POST, 
#                 self.request.FILES, 
#                 instance=self.object
#             )
#         else:
#             context['image_formset'] = HostelImageFormSet(instance=self.object)
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         image_formset = context['image_formset']
        
#         with transaction.atomic():
#             self.object = form.save()
            
#             if image_formset.is_valid():
#                 image_formset.save()
        
#         messages.success(self.request, 'Hostel updated successfully!')
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('hostels:hostel-detail', kwargs={'slug': self.object.slug})


# class HostelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     """Delete hostel - only for hostel owner"""
#     model = Hostel
#     template_name = 'hostels/hostel_delete.html'
#     slug_field = 'slug'
#     slug_url_kwarg = 'slug'
#     success_url = reverse_lazy('hostels:dashboard')

#     def test_func(self):
#         return self.get_object().owner == self.request.user

#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'Hostel deleted successfully!')
#         return super().delete(request, *args, **kwargs)


# class RoomTypeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
#     """Create room type for a hostel"""
#     model = RoomType
#     form_class = RoomTypeForm
#     template_name = 'hostels/roomtype_form.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.hostel = get_object_or_404(Hostel, slug=kwargs['hostel_slug'])
#         return super().dispatch(request, *args, **kwargs)

#     def test_func(self):
#         return self.hostel.owner == self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['hostel'] = self.hostel
#         context['is_new_hostel'] = self.request.GET.get('new_hostel') == '1'
        
#         if self.request.POST:
#             context['image_formset'] = RoomTypeImageFormSet(self.request.POST, self.request.FILES)
#         else:
#             context['image_formset'] = RoomTypeImageFormSet()
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         image_formset = context['image_formset']
#         is_new_hostel = context['is_new_hostel']
        
#         with transaction.atomic():
#             form.instance.hostel = self.hostel
#             self.object = form.save()
            
#             if image_formset.is_valid():
#                 image_formset.instance = self.object
#                 image_formset.save()
        
#         if is_new_hostel:
#             messages.success(
#                 self.request, 
#                 'Room type added successfully! You can add more room types or finish setup.'
#             )
#         else:
#             messages.success(self.request, 'Room type created successfully!')
        
#         return super().form_valid(form)

#     def get_success_url(self):
#         is_new_hostel = self.request.GET.get('new_hostel') == '1'
        
#         if is_new_hostel:
#             # For new hostels, redirect to add another room type or finish
#             return reverse('hostels:roomtype-create', kwargs={'hostel_slug': self.hostel.slug}) + '?new_hostel=1&continue=1'
#         else:
#             return reverse('hostels:hostel-detail', kwargs={'slug': self.hostel.slug})


# class RoomTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     """Update room type"""
#     model = RoomType
#     form_class = RoomTypeForm
#     template_name = 'hostels/roomtype_update.html'

#     def test_func(self):
#         return self.get_object().hostel.owner == self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['hostel'] = self.object.hostel
#         if self.request.POST:
#             context['image_formset'] = RoomTypeImageFormSet(
#                 self.request.POST, 
#                 self.request.FILES, 
#                 instance=self.object
#             )
#         else:
#             context['image_formset'] = RoomTypeImageFormSet(instance=self.object)
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         image_formset = context['image_formset']
        
#         with transaction.atomic():
#             self.object = form.save()
            
#             if image_formset.is_valid():
#                 image_formset.save()
        
#         messages.success(self.request, 'Room type updated successfully!')
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})


# class RoomTypeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     """Delete room type"""
#     model = RoomType
#     template_name = 'hostels/roomtype_delete.html'

#     def test_func(self):
#         return self.get_object().hostel.owner == self.request.user

#     def get_success_url(self):
#         return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})

#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'Room type deleted successfully!')
#         return super().delete(request, *args, **kwargs)


# class DashboardView(LoginRequiredMixin, ListView):
#     """Owner dashboard to manage their hostels"""
#     template_name = 'hostels/dashboard.html'
#     context_object_name = 'hostels'
#     paginate_by = 10

#     def get_queryset(self):
#         return Hostel.objects.filter(owner=self.request.user).with_stats()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get summary stats
#         user_hostels = Hostel.objects.filter(owner=self.request.user)
#         context['total_hostels'] = user_hostels.count()
#         context['total_inquiries'] = ContactInquiry.objects.filter(
#             hostel__owner=self.request.user
#         ).count()
#         context['new_inquiries'] = ContactInquiry.objects.filter(
#             hostel__owner=self.request.user,
#             status='new'
#         ).count()
        
#         return context


# class ContactInquiryCreateView(CreateView):
#     """Create contact inquiry - AJAX view"""
#     model = ContactInquiry
#     form_class = ContactInquiryForm

#     def form_valid(self, form):
#         hostel = get_object_or_404(Hostel, slug=self.kwargs['hostel_slug'])
#         form.instance.hostel = hostel
        
#         if self.request.user.is_authenticated:
#             form.instance.user = self.request.user
        
#         self.object = form.save()
        
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Your inquiry has been sent successfully! The hostel owner will contact you soon.'
#             })
#         else:
#             messages.success(
#                 self.request, 
#                 'Your inquiry has been sent successfully! The hostel owner will contact you soon.'
#             )
#             return redirect('hostels:hostel-detail', slug=hostel.slug)

#     def form_invalid(self, form):
#         if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': False,
#                 'errors': form.errors
#             })
#         else:
#             return super().form_invalid(form)


# class InquiryListView(LoginRequiredMixin, ListView):
#     """List inquiries for hostel owner"""
#     model = ContactInquiry
#     template_name = 'hostels/inquiry_list.html'
#     context_object_name = 'inquiries'
#     paginate_by = 20

#     def get_queryset(self):
#         return ContactInquiry.objects.filter(
#             hostel__owner=self.request.user
#         ).select_related('hostel', 'room_type_interest', 'school')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Filter options
#         status_filter = self.request.GET.get('status')
#         if status_filter:
#             context['inquiries'] = context['inquiries'].filter(status=status_filter)
        
#         context['status_choices'] = ContactInquiry.STATUS_CHOICES
#         context['current_status'] = status_filter
        
#         return context


# @method_decorator(login_required, name='dispatch')
# class InquiryDetailView(DetailView):
#     """Detailed view of inquiry for owner"""
#     model = ContactInquiry
#     template_name = 'hostels/inquiry_detail.html'
#     context_object_name = 'inquiry'

#     def get_queryset(self):
#         return ContactInquiry.objects.filter(
#             hostel__owner=self.request.user
#         ).select_related('hostel', 'room_type_interest', 'school', 'user')


# @require_POST
# @login_required
# def mark_inquiry_contacted(request, inquiry_id):
#     """Mark inquiry as contacted"""
#     inquiry = get_object_or_404(
#         ContactInquiry, 
#         id=inquiry_id, 
#         hostel__owner=request.user
#     )
    
#     inquiry.mark_as_contacted(user=request.user)
    
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({'success': True})
#     else:
#         messages.success(request, 'Inquiry marked as contacted.')
#         return redirect('hostels:inquiry-detail', pk=inquiry.id)


# @login_required
# def finish_hostel_setup(request, hostel_slug):
#     """Complete hostel setup after adding room types"""
#     hostel = get_object_or_404(Hostel, slug=hostel_slug, owner=request.user)
    
#     # Check if hostel has at least one room type
#     if hostel.room_types.count() == 0:
#         messages.warning(
#             request, 
#             'Please add at least one room type to complete your hostel setup.'
#         )
#         return redirect('hostels:roomtype-create', hostel_slug=hostel.slug)
    
#     messages.success(
#         request, 
#         f'Congratulations! Your hostel "{hostel.name}" is now live and ready to receive bookings.'
#     )
#     return redirect('hostels:hostel-detail', slug=hostel.slug)
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from math import radians, cos, sin, asin, sqrt
import json

from .models import Hostel, RoomType, School, Amenity, HostelImage, RoomTypeImage, ContactInquiry
from .forms import (
    HostelCreateForm, HostelUpdateForm, RoomTypeForm, 
    ContactInquiryForm, HostelImageFormSet, RoomTypeImageFormSet
)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r


class HostelListView(ListView):
    """Public view for students to browse hostels"""
    model = Hostel
    template_name = 'hostels/hostel_list.html'
    context_object_name = 'hostels'
    paginate_by = 12

    def get_queryset(self):
        queryset = Hostel.active.all().with_stats()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.search(search_query)
        
        # Filter by school
        school_id = self.request.GET.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(max_price__lte=max_price)
        
        # Filter by amenities
        amenities = self.request.GET.getlist('amenities')
        if amenities:
            queryset = queryset.filter(amenities__in=amenities).distinct()
        
        # Filter by wifi
        has_wifi = self.request.GET.get('has_wifi')
        if has_wifi == 'true':
            queryset = queryset.filter(has_wifi=True)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-is_featured')
        if sort_by == 'price_low':
            queryset = queryset.order_by('min_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-min_price')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-is_featured', '-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schools'] = School.active.all()
        context['amenities'] = Amenity.active.all()
        
        # Calculate distances for each hostel if school is selected
        school_id = self.request.GET.get('school')
        if school_id:
            try:
                school = School.objects.get(id=school_id)
                if school.latitude and school.longitude:
                    for hostel in context['hostels']:
                        if hostel.latitude and hostel.longitude:
                            distance = calculate_distance(
                                float(school.latitude), float(school.longitude),
                                float(hostel.latitude), float(hostel.longitude)
                            )
                            hostel.distance_to_school = round(distance, 1) if distance else None
                        else:
                            hostel.distance_to_school = None
            except School.DoesNotExist:
                pass
        
        # Preserve filters in context
        context['current_search'] = self.request.GET.get('search', '')
        context['current_school'] = self.request.GET.get('school', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_amenities'] = self.request.GET.getlist('amenities')
        context['current_wifi'] = self.request.GET.get('has_wifi', '')
        context['current_sort'] = self.request.GET.get('sort', '-is_featured')
        
        return context


class HostelDetailView(DetailView):
    """Detailed view of a hostel for students"""
    model = Hostel
    template_name = 'hostels/hostel_detail.html'
    context_object_name = 'hostel'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Hostel.active.all().select_related('school', 'owner').prefetch_related(
            'amenities',
            'images',
            Prefetch('room_types', queryset=RoomType.objects.prefetch_related('images'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_form'] = ContactInquiryForm(hostel=self.object)
        context['similar_hostels'] = Hostel.active.all().filter(
            school=self.object.school
        ).exclude(id=self.object.id)[:4]
        
        # Calculate distance to school if coordinates are available
        hostel = self.object
        school = hostel.school
        if (hostel.latitude and hostel.longitude and 
            school.latitude and school.longitude):
            distance = calculate_distance(
                float(school.latitude), float(school.longitude),
                float(hostel.latitude), float(hostel.longitude)
            )
            context['distance_to_school'] = round(distance, 1) if distance else None
        
        return context


class HostelCreateView(LoginRequiredMixin, CreateView):
    """Create new hostel - for authenticated users"""
    model = Hostel
    form_class = HostelCreateForm
    template_name = 'hostels/hostel_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = HostelImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = HostelImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        print(form)
        with transaction.atomic():
            form.instance.owner = self.request.user
            form.instance.owner_name = self.request.user.full_name or self.request.user.email
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
        
        messages.success(self.request, 'Hostel created successfully! Now add your room types.')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to room type creation with a flag to indicate it's a new hostel
        return reverse('hostels:roomtype-create', kwargs={'hostel_slug': self.object.slug}) + '?new_hostel=1'


class HostelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update hostel - only for hostel owner"""
    model = Hostel
    form_class = HostelUpdateForm
    template_name = 'hostels/hostel_update.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        return self.get_object().owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = HostelImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = HostelImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.save()
        
        messages.success(self.request, 'Hostel updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('hostels:hostel-detail', kwargs={'slug': self.object.slug})


class HostelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete hostel - only for hostel owner"""
    model = Hostel
    template_name = 'hostels/hostel_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('hostels:dashboard')

    def test_func(self):
        return self.get_object().owner == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Hostel deleted successfully!')
        return super().delete(request, *args, **kwargs)


class RoomTypeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create room type for a hostel"""
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'hostels/roomtype_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.hostel = get_object_or_404(Hostel, slug=kwargs['hostel_slug'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.hostel.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel'] = self.hostel
        context['is_new_hostel'] = self.request.GET.get('new_hostel') == '1'
        
        if self.request.POST:
            context['image_formset'] = RoomTypeImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = RoomTypeImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        is_new_hostel = context['is_new_hostel']
        
        with transaction.atomic():
            form.instance.hostel = self.hostel
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
        
        if is_new_hostel:
            messages.success(
                self.request, 
                'Room type added successfully! You can add more room types or finish setup.'
            )
        else:
            messages.success(self.request, 'Room type created successfully!')
        
        return super().form_valid(form)

    def get_success_url(self):
        is_new_hostel = self.request.GET.get('new_hostel') == '1'
        
        if is_new_hostel:
            # For new hostels, redirect to add another room type or finish
            return reverse('hostels:roomtype-create', kwargs={'hostel_slug': self.hostel.slug}) + '?new_hostel=1&continue=1'
        else:
            return reverse('hostels:hostel-detail', kwargs={'slug': self.hostel.slug})


class RoomTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update room type"""
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'hostels/roomtype_update.html'

    def test_func(self):
        return self.get_object().hostel.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel'] = self.object.hostel
        if self.request.POST:
            context['image_formset'] = RoomTypeImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = RoomTypeImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.save()
        
        messages.success(self.request, 'Room type updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})


class RoomTypeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete room type"""
    model = RoomType
    template_name = 'hostels/roomtype_delete.html'

    def test_func(self):
        return self.get_object().hostel.owner == self.request.user

    def get_success_url(self):
        return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Room type deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, ListView):
    """Owner dashboard to manage their hostels"""
    template_name = 'hostels/dashboard.html'
    context_object_name = 'hostels'
    paginate_by = 10

    def get_queryset(self):
        return Hostel.objects.filter(owner=self.request.user).with_stats()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get summary stats
        user_hostels = Hostel.objects.filter(owner=self.request.user)
        context['total_hostels'] = user_hostels.count()
        context['total_inquiries'] = ContactInquiry.objects.filter(
            hostel__owner=self.request.user
        ).count()
        context['new_inquiries'] = ContactInquiry.objects.filter(
            hostel__owner=self.request.user,
            status='new'
        ).count()
        
        return context


class HostelRoomTypesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View to manage room types for a hostel"""
    model = RoomType
    template_name = 'hostels/hostel_room_types.html'
    context_object_name = 'room_types'

    def dispatch(self, request, *args, **kwargs):
        self.hostel = get_object_or_404(Hostel, slug=kwargs['hostel_slug'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.hostel.owner == self.request.user

    def get_queryset(self):
        return self.hostel.room_types.all().prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel'] = self.hostel
        return context


class ContactInquiryCreateView(CreateView):
    """Create contact inquiry - AJAX view"""
    model = ContactInquiry
    form_class = ContactInquiryForm

    def form_valid(self, form):
        hostel = get_object_or_404(Hostel, slug=self.kwargs['hostel_slug'])
        form.instance.hostel = hostel
        
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        
        self.object = form.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Your inquiry has been sent successfully! The hostel owner will contact you soon.'
            })
        else:
            messages.success(
                self.request, 
                'Your inquiry has been sent successfully! The hostel owner will contact you soon.'
            )
            return redirect('hostels:hostel-detail', slug=hostel.slug)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        else:
            return super().form_invalid(form)


class InquiryListView(LoginRequiredMixin, ListView):
    """List inquiries for hostel owner"""
    model = ContactInquiry
    template_name = 'hostels/inquiry_list.html'
    context_object_name = 'inquiries'
    paginate_by = 20

    def get_queryset(self):
        return ContactInquiry.objects.filter(
            hostel__owner=self.request.user
        ).select_related('hostel', 'room_type_interest', 'school')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter options
        status_filter = self.request.GET.get('status')
        if status_filter:
            context['inquiries'] = context['inquiries'].filter(status=status_filter)
        
        context['status_choices'] = ContactInquiry.STATUS_CHOICES
        context['current_status'] = status_filter
        
        return context


@method_decorator(login_required, name='dispatch')
class InquiryDetailView(DetailView):
    """Detailed view of inquiry for owner"""
    model = ContactInquiry
    template_name = 'hostels/inquiry_detail.html'
    context_object_name = 'inquiry'

    def get_queryset(self):
        return ContactInquiry.objects.filter(
            hostel__owner=self.request.user
        ).select_related('hostel', 'room_type_interest', 'school', 'user')


@require_POST
@login_required
def mark_inquiry_contacted(request, inquiry_id):
    """Mark inquiry as contacted"""
    inquiry = get_object_or_404(
        ContactInquiry, 
        id=inquiry_id, 
        hostel__owner=request.user
    )
    
    inquiry.mark_as_contacted(user=request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    else:
        messages.success(request, 'Inquiry marked as contacted.')
        return redirect('hostels:inquiry-detail', pk=inquiry.id)


@login_required
def finish_hostel_setup(request, hostel_slug):
    """Complete hostel setup after adding room types"""
    hostel = get_object_or_404(Hostel, slug=hostel_slug, owner=request.user)
    
    # Check if hostel has at least one room type
    if hostel.room_types.count() == 0:
        messages.warning(
            request, 
            'Please add at least one room type to complete your hostel setup.'
        )
        return redirect('hostels:roomtype-create', hostel_slug=hostel.slug)
    
    messages.success(
        request, 
        f'Congratulations! Your hostel "{hostel.name}" is now live and ready to receive bookings.'
    )
    return redirect('hostels:hostel-detail', slug=hostel.slug)


@login_required
def get_current_location(request):
    """AJAX endpoint to save current location coordinates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                return JsonResponse({
                    'success': True,
                    'latitude': latitude,
                    'longitude': longitude,
                    'message': 'Location captured successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid coordinates received.'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })