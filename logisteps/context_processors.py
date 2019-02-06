from .models import LogistepsUser
from django.contrib.auth.models import User

def logistepsUser(request):
    if request.user.is_anonymous:
        logisetpsUser = None
    else:
        logisetpsUser = LogistepsUser.objects.get(user_id=request.user.id)
    
    return {
        'logistepsUser': logisetpsUser
    }