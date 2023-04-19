from celery import shared_task


@shared_task
def add_after_expiry_task(pk, hostel):
    '''
    get the number of rooms in a hostel and add 1 if the rent expires
    '''
    hostel.no_of_rooms += 1
    hostel.save()
