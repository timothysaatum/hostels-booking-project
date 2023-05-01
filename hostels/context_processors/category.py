from hostels.models import Hostel
def category():
    cat = Hostel.objects.all()
    return {'cat':cat}