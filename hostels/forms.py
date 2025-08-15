from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import (
    Hostel, RoomType, Room, School, Amenity, 
    HostelImage, RoomTypeImage, ContactInquiry
)


class HostelCreateForm(forms.ModelForm):
    """Enhanced form for creating hostels"""
    
    class Meta:
        model = Hostel
        fields = [
            'school', 'campus', 'name', 'description', 'phone_number', 'email',
            'latitude', 'longitude', 'address', 'account_number', 'account_name',
            'bank_name', 'main_image', 'amenities', 'has_wifi',
            'total_rooms', 'available_rooms', 'min_price', 'max_price'
        ]
        widgets = {
            'school': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Select school'
            }),
            'campus': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main Campus, North Campus'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hostel name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your hostel...'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +233 20 123 4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@hostel.com'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5.6037',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '-0.1870',
                'step': 'any'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address of the hostel'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank account number'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account holder name'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank name'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'has_wifi': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'total_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Total number of rooms'
            }),
            'available_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Number of available rooms'
            }),
            'min_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Minimum price per person'
            }),
            'max_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Maximum price per person'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.active.all()
        self.fields['amenities'].queryset = Amenity.active.all()
        
        # Make certain fields required
        self.fields['school'].required = True
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['phone_number'].required = True
        self.fields['address'].required = True
        self.fields['account_name'].required = True
        self.fields['total_rooms'].required = True
        self.fields['available_rooms'].required = True
        self.fields['min_price'].required = True
        self.fields['max_price'].required = True

    def clean(self):
        cleaned_data = super().clean()
        total_rooms = cleaned_data.get('total_rooms')
        available_rooms = cleaned_data.get('available_rooms')
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        # Validate room counts
        if total_rooms is not None and available_rooms is not None:
            if available_rooms > total_rooms:
                raise ValidationError({
                    'available_rooms': 'Available rooms cannot exceed total rooms.'
                })
        
        # Validate price range
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValidationError({
                    'max_price': 'Maximum price must be greater than or equal to minimum price.'
                })
        
        return cleaned_data


class HostelUpdateForm(HostelCreateForm):
    """Form for updating hostels - same as create but with different validation"""
    
    class Meta(HostelCreateForm.Meta):
        # Add additional fields that can be updated
        fields = HostelCreateForm.Meta.fields + [
            'is_featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            **HostelCreateForm.Meta.widgets,
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO title (optional)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'SEO description (optional)'
            }),
        }


class RoomTypeForm(forms.ModelForm):
    """Form for creating/updating room types"""
    
    class Meta:
        model = RoomType
        fields = [
            'name', 'room_type', 'beds_per_room', 'total_rooms', 
            'price_per_person', 'description', 'main_image',
            'has_private_bathroom', 'has_balcony', 'has_ac', 
            'has_study_desk', 'has_wardrobe'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Standard Single Room'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'beds_per_room': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 8
            }),
            'total_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'price_per_person': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this room type...'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'has_private_bathroom': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_balcony': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_ac': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_study_desk': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_wardrobe': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        room_type = cleaned_data.get('room_type')
        beds_per_room = cleaned_data.get('beds_per_room')
        
        # Auto-set beds_per_room based on room_type if not custom
        if room_type and room_type != 'custom':
            expected_beds = {
                'single': 1,
                'double': 2,
                'triple': 3,
                'quad': 4,
            }.get(room_type)
            
            if expected_beds and beds_per_room != expected_beds:
                cleaned_data['beds_per_room'] = expected_beds
        
        return cleaned_data


class ContactInquiryForm(forms.ModelForm):
    """Form for contact inquiries from students"""
    
    class Meta:
        model = ContactInquiry
        fields = [
            'name', 'email', 'phone_number', 'student_id', 'school',
            'room_type_interest', 'number_of_occupants', 
            'preferred_move_in_date', 'message'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+233 20 123 4567',
                'required': True
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your student ID (optional)'
            }),
            'school': forms.Select(attrs={
                'class': 'form-select'
            }),
            'room_type_interest': forms.Select(attrs={
                'class': 'form-select'
            }),
            'number_of_occupants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'preferred_move_in_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any specific questions or requirements...'
            }),
        }

    def __init__(self, *args, **kwargs):
        hostel = kwargs.pop('hostel', None)
        super().__init__(*args, **kwargs)
        
        self.fields['school'].queryset = School.active.all()
        self.fields['school'].required = False
        
        if hostel:
            self.fields['room_type_interest'].queryset = hostel.room_types.all()
            self.fields['room_type_interest'].empty_label = "Any room type"
        else:
            self.fields['room_type_interest'].queryset = RoomType.objects.none()
        
        self.fields['room_type_interest'].required = False


class HostelImageForm(forms.ModelForm):
    """Form for hostel images"""
    
    class Meta:
        model = HostelImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class RoomTypeImageForm(forms.ModelForm):
    """Form for room type images"""
    
    class Meta:
        model = RoomTypeImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class RoomForm(forms.ModelForm):
    """Form for creating/updating individual rooms"""
    
    class Meta:
        model = Room
        fields = [
            'room_number', 'floor_number', 'capacity', 
            'occupant_gender', 'is_available', 'notes'
        ]
        widgets = {
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A101'
            }),
            'floor_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'occupant_gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes (optional)'
            }),
        }


# Enhanced Formsets for handling more images
HostelImageFormSet = inlineformset_factory(
    Hostel, HostelImage, 
    form=HostelImageForm, 
    extra=10,  # Increased from 3 to 10
    can_delete=True,
    max_num=20  # Allow up to 20 images
)

RoomTypeImageFormSet = inlineformset_factory(
    RoomType, RoomTypeImage, 
    form=RoomTypeImageForm, 
    extra=5,  # Increased for more images
    can_delete=True,
    max_num=15  # Allow up to 15 images per room type
)


class HostelSearchForm(forms.Form):
    """Form for searching hostels"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search hostels, schools, locations...'
        })
    )
    school = forms.ModelChoiceField(
        queryset=School.active.all(),
        required=False,
        empty_label="All Schools",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'min': 0,
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'min': 0,
            'step': '0.01'
        })
    )
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.active.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    has_wifi = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-is_featured', 'Featured First'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('-rating', 'Highest Rated'),
            ('-created_at', 'Newest First'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )