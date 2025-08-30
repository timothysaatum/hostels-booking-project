import math
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Prefetch, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.cache import cache
# from django.utils.cache import cache_page
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import json
import logging
from .models import Hostel, RoomType, School, Amenity, ContactInquiry, calculate_distance
from .forms import (
    HostelCreateForm, HostelUpdateForm, RoomTypeForm, 
    ContactInquiryForm, HostelImageFormSet, RoomTypeImageFormSet
)
from django.db import models

logger = logging.getLogger(__name__)
# class HostelListView(ListView):
#     """Public view for students to browse hostels with distance calculation"""
#     model = Hostel
#     template_name = 'hostels/hostel_list.html'
#     context_object_name = 'hostels'
#     paginate_by = 12

#     def get_queryset(self):
#         queryset = Hostel.active.all().with_stats().select_related('school')

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
#             try:
#                 queryset = queryset.filter(min_price__gte=float(min_price))
#             except (ValueError, TypeError):
#                 pass
#         if max_price:
#             try:
#                 queryset = queryset.filter(max_price__lte=float(max_price))
#             except (ValueError, TypeError):
#                 pass

#         # Filter by amenities
#         amenities = self.request.GET.getlist('amenities')
#         if amenities:
#             queryset = queryset.filter(amenities__in=amenities).distinct()

#         # Filter by wifi
#         has_wifi = self.request.GET.get('has_wifi')
#         if has_wifi == 'true':
#             queryset = queryset.filter(has_wifi=True)

#         # Add distance calculation if school is selected
#         if school_id:
#             try:
#                 school = School.objects.get(id=school_id)
#                 if school.latitude and school.longitude:
#                     # Use database-level distance calculation for performance
#                     queryset = queryset.extra(
#                         select={
#                             'distance_to_school': """
#                                 CASE
#                                     WHEN hostels_hostel.latitude IS NOT NULL
#                                     AND hostels_hostel.longitude IS NOT NULL
#                                     THEN
#                                         6371 * acos(
#                                             LEAST(1.0, GREATEST(-1.0,
#                                                 cos(radians(%s))
#                                                 * cos(radians(hostels_hostel.latitude))
#                                                 * cos(radians(hostels_hostel.longitude) - radians(%s))
#                                                 + sin(radians(%s))
#                                                 * sin(radians(hostels_hostel.latitude))
#                                             ))
#                                         )
#                                     ELSE NULL
#                                 END
#                             """
#                         },
#                         select_params=[
#                             float(school.latitude), float(school.longitude),
#                             float(school.latitude)
#                         ]
#                     )
#             except (School.DoesNotExist, ValueError, TypeError):
#                 pass

#         # Sorting
#         sort_by = self.request.GET.get('sort', '-is_featured')
#         if sort_by == 'price_low':
#             queryset = queryset.order_by('min_price', '-is_featured')
#         elif sort_by == 'price_high':
#             queryset = queryset.order_by('-min_price', '-is_featured')
#         elif sort_by == 'rating':
#             queryset = queryset.order_by('-rating', '-is_featured')
#         elif sort_by == 'newest':
#             queryset = queryset.order_by('-created_at')
#         elif sort_by == 'distance' and school_id:
#             queryset = queryset.extra(order_by=['distance_to_school'])
#         else:
#             queryset = queryset.order_by('-is_featured', '-created_at')

#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['schools'] = School.active.all()
#         context['amenities'] = Amenity.active.all()

#         # Add distance to each hostel if school is selected
#         school_id = self.request.GET.get('school')
#         if school_id and hasattr(context['hostels'], '__iter__'):
#             try:
#                 school = School.objects.get(id=school_id)
#                 if school.latitude and school.longitude:
#                     for hostel in context['hostels']:
#                         # Check if distance was calculated at database level
#                         if hasattr(hostel, 'distance_to_school') and hostel.distance_to_school:
#                             hostel.distance_display = f"{hostel.distance_to_school:.1f} km"
#                         elif hasattr(hostel, 'distance_to_school'):
#                             # Fallback to Python calculation
#                             distance = calculate_distance(
#                                 school.latitude, school.longitude,
#                                 hostel.latitude, hostel.longitude
#                             )
#                             hostel.distance_display = f"{distance:.1f} km" if distance else "Distance unknown"
#                         else:
#                             hostel.distance_display = "Distance unknown"
#             except School.DoesNotExist:
#                 pass


#         # Preserve filters in context
#         context['current_search'] = self.request.GET.get('search', '')
#         context['current_school'] = self.request.GET.get('school', '')
#         context['current_min_price'] = self.request.GET.get('min_price', '')
#         context['current_max_price'] = self.request.GET.get('max_price', '')
#         context['current_amenities'] = self.request.GET.getlist('amenities')
#         context['current_wifi'] = self.request.GET.get('has_wifi', '')
#         context['current_sort'] = self.request.GET.get('sort', '-is_featured')
#         print(context['hostels'])
#         return context
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    if not all([lat1, lon1, lat2, lon2]):
        return None

    try:
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(
            math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)]
        )

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers
        r = 6371
        return r * c

    except (ValueError, TypeError, OverflowError):
        return None


class HostelListView(ListView):
    """
    Public view for students to browse hostels with comprehensive filtering,
    search functionality, and distance calculation from selected schools.
    Uses Python-only distance calculation for database compatibility.
    """

    model = Hostel
    template_name = "hostels/hostel_list.html"
    context_object_name = "hostels"
    paginate_by = 12

    # Default sorting options
    SORT_OPTIONS = {
        "price_low": ("min_price", "-is_featured"),
        "price_high": ("-min_price", "-is_featured"),
        "rating": ("-rating", "-is_featured"),
        "newest": ("-created_at",),
        "default": ("-is_featured", "-created_at"),
    }

    def get_queryset(self):
        """Build filtered and sorted queryset based on request parameters"""
        try:
            queryset = Hostel.active.all().with_stats().select_related("school")

            # Apply filters in sequence
            queryset = self._apply_search_filter(queryset)
            queryset = self._apply_school_filter(queryset)
            queryset = self._apply_price_filters(queryset)
            queryset = self._apply_amenity_filters(queryset)
            queryset = self._apply_wifi_filter(queryset)
            queryset = self._apply_basic_sorting(queryset)

            return queryset

        except Exception as e:
            logger.error(f"Error in HostelListView.get_queryset: {e}")
            # Return basic queryset as fallback
            return (
                Hostel.active.all()
                .select_related("school")
                .order_by("-is_featured", "-created_at")
            )

    def _apply_search_filter(self, queryset):
        """Apply search functionality to queryset"""
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.search(search_query)
        return queryset

    def _apply_school_filter(self, queryset):
        """Filter hostels by selected school"""
        school_id = self.request.GET.get("school", "").strip()
        if school_id and school_id.isdigit():
            queryset = queryset.filter(school_id=int(school_id))
        return queryset

    def _apply_price_filters(self, queryset):
        """Apply minimum and maximum price filters"""
        min_price = self._get_float_param("min_price")
        max_price = self._get_float_param("max_price")

        if min_price is not None and min_price >= 0:
            queryset = queryset.filter(min_price__gte=min_price)

        if max_price is not None and max_price >= 0:
            queryset = queryset.filter(max_price__lte=max_price)

        return queryset

    def _apply_amenity_filters(self, queryset):
        """Filter hostels by selected amenities"""
        amenities = self.request.GET.getlist("amenities")
        # Filter out empty strings and validate
        amenities = [a for a in amenities if a and a.isdigit()]

        if amenities:
            # Convert to integers
            amenity_ids = [int(a) for a in amenities]
            queryset = queryset.filter(amenities__id__in=amenity_ids).distinct()

        return queryset

    def _apply_wifi_filter(self, queryset):
        """Filter hostels by WiFi availability"""
        has_wifi = self.request.GET.get("has_wifi", "").strip().lower()
        if has_wifi == "true":
            queryset = queryset.filter(has_wifi=True)
        elif has_wifi == "false":
            queryset = queryset.filter(has_wifi=False)

        return queryset

    def _apply_basic_sorting(self, queryset):
        """Apply basic sorting (distance sorting handled in get_context_data)"""
        sort_by = self.request.GET.get("sort", "default").strip()

        # Skip distance sorting here - it's handled after distance calculation
        if sort_by == "distance":
            return queryset.order_by("-is_featured", "-created_at")

        # Get sort fields from SORT_OPTIONS
        sort_fields = self.SORT_OPTIONS.get(sort_by, self.SORT_OPTIONS["default"])
        return queryset.order_by(*sort_fields)

    def get_context_data(self, **kwargs):
        """Add additional context data for template rendering"""
        context = super().get_context_data(**kwargs)

        try:
            # Add cached reference data
            context["schools"] = self._get_cached_schools()
            context["amenities"] = self._get_cached_amenities()

            # Calculate distances and add display
            self._calculate_and_add_distances(context)

            # Apply distance-based sorting if requested
            self._apply_distance_sorting(context)

            # Preserve current filter values
            context.update(self._get_current_filters())

            # Add sort options for template
            context["sort_options"] = self._get_sort_options_for_template()

        except Exception as e:
            logger.error(f"Error in HostelListView.get_context_data: {e}")
            # Ensure basic context is available
            context.setdefault("schools", School.active.all())
            context.setdefault("amenities", Amenity.active.all())

        return context

    def _calculate_and_add_distances(self, context):
        """Calculate distances and add display to each hostel"""
        school_id = self.request.GET.get("school", "").strip()

        if not (
            school_id
            and school_id.isdigit()
            and hasattr(context["hostels"], "__iter__")
        ):
            # No school selected or no hostels - set default values
            for hostel in context["hostels"]:
                hostel.distance_to_school = None
                hostel.distance_display = "Select a school to see distance"
            return

        try:
            school = self._get_cached_school(int(school_id))
            if not (school and school.latitude and school.longitude):
                # School has no coordinates
                for hostel in context["hostels"]:
                    hostel.distance_to_school = None
                    hostel.distance_display = "School location not available"
                return

            # Calculate distance for each hostel
            for hostel in context["hostels"]:
                if hostel.latitude and hostel.longitude:
                    distance = calculate_distance(
                        school.latitude,
                        school.longitude,
                        hostel.latitude,
                        hostel.longitude,
                    )
                    if distance is not None:
                        hostel.distance_to_school = distance
                        hostel.distance_display = f"{distance:.1f} km"
                    else:
                        hostel.distance_to_school = None
                        hostel.distance_display = "Distance calculation error"
                else:
                    hostel.distance_to_school = None
                    hostel.distance_display = "Hostel location not available"

        except (School.DoesNotExist, Exception) as e:
            logger.warning(f"Error calculating distances: {e}")
            # Set default values for all hostels in case of error
            for hostel in context["hostels"]:
                hostel.distance_to_school = None
                hostel.distance_display = "Distance calculation error"

    def _apply_distance_sorting(self, context):
        """Sort hostels by distance if distance sorting is requested"""
        sort_by = self.request.GET.get("sort", "default").strip()

        if sort_by == "distance" and hasattr(context["hostels"], "__iter__"):
            # Convert to list if it's a queryset
            hostels_list = list(context["hostels"])

            # Sort by distance (None values at the end)
            hostels_list.sort(
                key=lambda h: (
                    h.distance_to_school is None,  # None values go to end
                    (
                        h.distance_to_school
                        if h.distance_to_school is not None
                        else float("inf")
                    ),
                )
            )

            # Update the context with sorted list
            context["hostels"] = hostels_list

    def _get_current_filters(self):
        """Get current filter values to preserve in template"""
        return {
            "current_search": self.request.GET.get("search", ""),
            "current_school": self.request.GET.get("school", ""),
            "current_min_price": self.request.GET.get("min_price", ""),
            "current_max_price": self.request.GET.get("max_price", ""),
            "current_amenities": self.request.GET.getlist("amenities"),
            "current_wifi": self.request.GET.get("has_wifi", ""),
            "current_sort": self.request.GET.get("sort", "default"),
        }

    def _get_sort_options_for_template(self):
        """Get sort options for template dropdown"""
        return [
            ("default", "Featured First"),
            ("price_low", "Price: Low to High"),
            ("price_high", "Price: High to Low"),
            ("rating", "Highest Rated"),
            ("newest", "Newest First"),
            ("distance", "Distance (requires school selection)"),
        ]

    def _get_cached_schools(self):
        """Get schools with caching"""
        return cache.get_or_set(
            "active_schools",
            lambda: list(School.active.all().order_by("name")),
            timeout=3600,  # Cache for 1 hour
        )

    def _get_cached_amenities(self):
        """Get amenities with caching"""
        return cache.get_or_set(
            "active_amenities",
            lambda: list(Amenity.active.all().order_by("name")),
            timeout=3600,  # Cache for 1 hour
        )

    def _get_cached_school(self, school_id):
        """Get a specific school with caching"""
        cache_key = f"school_{school_id}"
        return cache.get_or_set(
            cache_key,
            lambda: School.objects.get(id=school_id),
            timeout=3600,  # Cache for 1 hour
        )

    def _get_float_param(self, param_name):
        """Safely convert request parameter to float"""
        value = self.request.GET.get(param_name, "").strip()
        if not value:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid float parameter {param_name}: {value}")
            return None


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
        hostel = self.object
        
        # Initialize contact form
        context['contact_form'] = ContactInquiryForm(hostel=hostel)
        
        # Calculate distance to school
        if (hostel.latitude and hostel.longitude and 
            hostel.school.latitude and hostel.school.longitude):
            distance = calculate_distance(
                hostel.school.latitude, hostel.school.longitude,
                hostel.latitude, hostel.longitude
            )
            context['distance_to_school'] = distance
        
        # Get similar hostels with distance calculation
        similar_hostels = Hostel.active.all().filter(
            school=hostel.school
        ).exclude(id=hostel.id)[:4]
        
        # Add distance to similar hostels
        for similar in similar_hostels:
            if (similar.latitude and similar.longitude and 
                hostel.school.latitude and hostel.school.longitude):
                distance = calculate_distance(
                hostel.school.latitude, hostel.school.longitude,
                similar.latitude, similar.longitude
            )
            similar._distance_to_school = distance  # note the underscore

        context['similar_hostels'] = similar_hostels
        return context


class HostelCreateView(LoginRequiredMixin, CreateView):
    """Create new hostel with automatic room generation"""
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
        
        with transaction.atomic():
            form.instance.owner = self.request.user
            form.instance.owner_name = (
                f"{self.request.user.first_name} {self.request.user.last_name}".strip() 
                or self.request.user.username
            )
            self.object = form.save()
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
        
        messages.success(self.request, 'Hostel created successfully! Now add your room types.')
        return super().form_valid(form)

    def get_success_url(self):
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
    """Create room type with automatic room generation"""
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
            self.object = form.save()  # This will automatically create rooms via the save method
            
            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
        
        if is_new_hostel:
            messages.success(
                self.request, 
                f'Room type added successfully with {self.object.total_rooms} rooms created! '
                'You can add more room types or finish setup.'
            )
        else:
            messages.success(
                self.request, 
                f'Room type created successfully with {self.object.total_rooms} rooms!'
            )
        
        return super().form_valid(form)

    def get_success_url(self):
        is_new_hostel = self.request.GET.get('new_hostel') == '1'
        
        if is_new_hostel:
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
            # Check if total_rooms changed
            original_total_rooms = RoomType.objects.get(pk=self.object.pk).total_rooms
            new_total_rooms = form.cleaned_data['total_rooms']
            
            self.object = form.save()
            
            # Handle room creation/deletion if total_rooms changed
            if new_total_rooms != original_total_rooms:
                self._adjust_rooms(new_total_rooms, original_total_rooms)
            
            if image_formset.is_valid():
                image_formset.save()
        
        messages.success(self.request, 'Room type updated successfully!')
        return super().form_valid(form)

    def _adjust_rooms(self, new_total, original_total):
        """Adjust room count when total_rooms is updated"""
        current_rooms = self.object.rooms.count()
        
        if new_total > current_rooms:
            # Create additional rooms
            rooms_to_create = new_total - current_rooms
            existing_room_numbers = set(
                self.object.rooms.values_list('room_number', flat=True)
            )
            
            new_rooms = []
            for i in range(rooms_to_create):
                room_number = self.object._generate_room_number(existing_room_numbers)
                existing_room_numbers.add(room_number)
                
                from .models import Room
                room = Room(
                    room_type=self.object,
                    room_number=room_number,
                    floor_number=self.object._get_floor_from_room_number(room_number),
                    capacity=self.object.beds_per_room,
                    current_occupants=0,
                    is_available=True,
                    is_active=True
                )
                new_rooms.append(room)
            
            Room.objects.bulk_create(new_rooms, batch_size=50)
            
        elif new_total < current_rooms:
            # Remove excess rooms (only empty ones)
            excess_rooms = current_rooms - new_total
            rooms_to_delete = self.object.rooms.filter(
                current_occupants=0
            ).order_by('-created_at')[:excess_rooms]
            
            deleted_count = rooms_to_delete.count()
            rooms_to_delete.delete()
            
            if deleted_count < excess_rooms:
                messages.warning(
                    self.request,
                    f"Could only remove {deleted_count} empty rooms. "
                    f"{excess_rooms - deleted_count} rooms have occupants and couldn't be deleted."
                )

    def get_success_url(self):
        return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})


class RoomTypeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete room type"""
    model = RoomType
    template_name = 'hostels/roomtype_delete.html'

    def test_func(self):
        return self.get_object().hostel.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        room_type = self.get_object()
        occupied_rooms = room_type.rooms.filter(current_occupants__gt=0).count()
        
        if occupied_rooms > 0:
            messages.error(
                request, 
                f"Cannot delete room type. {occupied_rooms} rooms have current occupants."
            )
            return redirect('hostels:hostel-detail', slug=room_type.hostel.slug)
        
        messages.success(request, 'Room type and all associated rooms deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('hostels:hostel-detail', kwargs={'slug': self.object.hostel.slug})


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
        
        # Calculate total rooms and occupancy
        total_rooms = sum(hostel.total_rooms for hostel in user_hostels)
        total_occupied = sum(
            hostel.room_types.aggregate(
                occupied=models.Sum('rooms__current_occupants')
            )['occupied'] or 0 
            for hostel in user_hostels
        )
        
        context['total_rooms'] = total_rooms
        context['occupancy_rate'] = (
            (total_occupied / total_rooms * 100) if total_rooms > 0 else 0
        )
        
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
        return self.hostel.room_types.all().prefetch_related(
            'images',
            'rooms'
        ).annotate(
            total_capacity=F('total_rooms') * F('beds_per_room'),
            occupied_spots=models.Sum('rooms__current_occupants'),
            available_spots=F('total_capacity') - F('occupied_spots')
        )

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
        queryset = ContactInquiry.objects.filter(
            hostel__owner=self.request.user
        ).select_related('hostel', 'room_type_interest', 'school')
        
        # Apply filters
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        hostel_filter = self.request.GET.get('hostel')
        if hostel_filter:
            queryset = queryset.filter(hostel_id=hostel_filter)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ContactInquiry.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['user_hostels'] = Hostel.objects.filter(owner=self.request.user)
        context['current_hostel'] = self.request.GET.get('hostel', '')
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
    
    if hostel.room_types.count() == 0:
        messages.warning(
            request, 
            'Please add at least one room type to complete your hostel setup.'
        )
        return redirect('hostels:roomtype-create', hostel_slug=hostel.slug)
    
    # Update cached fields
    hostel.update_cached_fields()
    
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


@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('User-Agent')
def hostel_stats_api(request):
    """API endpoint for hostel statistics"""
    stats = cache.get('hostel_stats')
    
    if not stats:
        stats = {
            'total_hostels': Hostel.active.all().count(),
            'total_schools': School.active.all().count(),
            'total_rooms': sum(
                hostel.total_rooms for hostel in Hostel.active.all()
            ),
            'average_price': Hostel.active.all().aggregate(
                avg_min=models.Avg('min_price'),
                avg_max=models.Avg('max_price')
            ),
        }
        cache.set('hostel_stats', stats, 60 * 30)  # Cache for 30 minutes
    
    return JsonResponse(stats)


def ajax_room_types_by_hostel(request, hostel_id):
    """AJAX endpoint to get room types for a specific hostel"""
    try:
        hostel = Hostel.objects.get(id=hostel_id)
        room_types = hostel.room_types.all().values(
            'id', 'name', 'room_type', 'beds_per_room', 'price_per_person'
        )
        return JsonResponse({
            'success': True,
            'room_types': list(room_types)
        })
    except Hostel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Hostel not found.'
        })
