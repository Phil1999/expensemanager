from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
# Create your views here.


def index(request):
    
    user_exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None
    
    if user_exists:
        user_preferences = UserPreference.objects.get(user=request.user)

    currency_data = []

    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
   # import pdb # Python debugger
    #pdb.set_trace()

    # read json file
    with open(file_path, 'r') as json_file: # With automatically closes the file for you
        data = json.load(json_file)

        for k,v in data.items():
            currency_data.append({'name': k, 'value': v})

    if request.method == 'GET':
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})

    else:
        currency = request.POST['currency']
        if user_exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency = currency)    
        
        messages.success(request, 'Changes successfully saved.')
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})