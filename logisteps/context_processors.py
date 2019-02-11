from .models import LogistepsUser
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

def logistepsUser(request):
    if request.user.is_anonymous:
        logisetpsUser = None
    else:
        try:
            logisetpsUser = LogistepsUser.objects.get(user_id=request.user.id)
        except ObjectDoesNotExist:
            logisetpsUser = None
    
    return {
        'logistepsUser': logisetpsUser
    }