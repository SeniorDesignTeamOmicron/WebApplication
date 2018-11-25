from django.http import HttpResponse

# Create your views here.
def index(Request):
    return HttpResponse("LogiSteps index page.")