from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

import json
import csv
import datetime
# Create your views here.


@login_required(login_url='/authentication/login') # Protect the route
def index(request):
    sources = Source.objects.all()
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = "USD - United States Dollar"
    income = UserIncome.objects.filter(owner=request.user)

    # Create Paginator
    paginator = Paginator(income, 10)
    page_number = request.GET.get('page') # When a page is formatted like domain/search/?page=1
    page_obj = paginator.get_page(page_number)

    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
        
    }
    return render(request, 'income/index.html', context)

@login_required(login_url='/authentication/login')
def add_income(request):
    
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount_earned']
        description = request.POST['description']
        date = request.POST['date']
        source = request.POST['source']

        if not amount:
            messages.error(request, "Please enter an amount.")
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, "Please enter a description.")
            return render(request, 'income/add_income.html', context)
        
        if not date:
            messages.error(request, "Please select a date.")
            return render(request, 'income/add_income.html', context)
        
        
        UserIncome.objects.create(owner = request.user, amount_earned=amount, description=description, date=date, source=source)
        messages.success(request, "Successfully Saved Income Record.")
        return redirect('income')

@login_required(login_url='/authentication/login')
def edit_income(request, id):
    sources = Source.objects.all()
    income = UserIncome.objects.get(pk=id)
    context = {
        'income': income,
        'values': income,
        'sources': sources,
        
    }
    
    if request.method == "GET":
        
        return render(request, 'income/edit_income.html', context)

    if request.method == "POST":

        amount = request.POST['amount_earned']
        description = request.POST['description']
        date = request.POST['date']
        source = request.POST['source']

        if not amount:
            messages.error(request, "Please enter an amount.")
            return render(request, 'income/edit_income.html', context)

        if not description:
            messages.error(request, "Please enter a description.")
            return render(request, 'income/edit_income.html', context)
        
        if not date:
            messages.error(request, "Please select a date.")
            return render(request, 'income/edit_income.html', context)
        
        income.owner = request.user
        income.amount_spent = amount
        income.date = date
        income.category = source
        income.save()
        messages.success(request, "Successfully Updated Income.")
        return redirect('income')

@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    user_id = str(income.id)
    user_desc = str(income.description)
    user_date = str(income.date)
    messages.success(request, "Successfully Deleted Income " + 
    user_id + ": '" + user_desc + "' on " + user_date)
    income.delete()
    return redirect('income')

@login_required(login_url='/authentication/login')
def search_income(request):
    if request.method == "POST":

        # There is a weird bug sometimes it prints duplicate when doing a search for 'WoW' when desc is 'wwwwow'
        query_str = json.loads(request.body).get('searchText', "")
        
        # ex: if query is 1000 then search for amount >1000
        incomes = \
            UserIncome.objects.filter(amount_earned__istartswith=query_str, owner=request.user) | \
            UserIncome.objects.filter(date__istartswith=query_str, owner=request.user) | \
            UserIncome.objects.filter(description__icontains=query_str, owner=request.user) | \
            UserIncome.objects.filter(source__icontains=query_str, owner=request.user)
        
        data = incomes.values()

        return JsonResponse(list(data), safe = False)

def export_csv(request):
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=Incomes' + str(datetime.datetime.now()) + '.csv'

    csv_writer = csv.writer(resp)
    csv_writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes:
        csv_writer.writerow([income.amount_earned, income.description, income.source, income.date])
    
    return resp