from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

@csrf_exempt
def dump(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return HttpResponse('Welcome to the logisteps API')

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)
        return HttpResponse('Success')
