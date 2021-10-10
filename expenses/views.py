from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference

import csv
import json
import datetime
# Create your views here.


@login_required(login_url='/authentication/login') # Protect the route
def index(request):
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = "USD - United States Dollar"
        
    expenses = Expense.objects.filter(owner=request.user)

    # Create Paginator
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page') # When a page is formatted like domain/search/?page=1
    page_obj = paginator.get_page(page_number)

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expense(request):
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount_spent']
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not amount:
            messages.error(request, "Please enter an amount.")
            return render(request, 'expenses/add_expense.html', context)

        if not description:
            messages.error(request, "Please enter a description.")
            return render(request, 'expenses/add_expense.html', context)
        
        if not date:
            messages.error(request, "Please select a date.")
            return render(request, 'expenses/add_expense.html', context)
        
        
        Expense.objects.create(owner = request.user, amount_spent=amount, description=description, date=date, category=category)
        messages.success(request, "Successfully Saved Expense.")
        return redirect('expenses')

@login_required(login_url='/authentication/login')
def edit_expense(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk=id)
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
        
    }
    
    if request.method == "GET":
        
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == "POST":

        amount = request.POST['amount_spent']
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not amount:
            messages.error(request, "Please enter an amount.")
            return render(request, 'expenses/edit_expense.html', context)

        if not description:
            messages.error(request, "Please enter a description.")
            return render(request, 'expenses/edit_expense.html', context)
        
        if not date:
            messages.error(request, "Please select a date.")
            return render(request, 'expenses/edit_expense.html', context)
        
        expense.owner = request.user
        expense.amount_spent = amount
        expense.date = date
        expense.category = category
        expense.save()
        messages.success(request, "Successfully Updated Expense.")
        return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    user_id = str(expense.id)
    user_desc = str(expense.description)
    user_date = str(expense.date)
    messages.success(request, "Successfully Deleted Expense " + 
    user_id + ": '" + user_desc + "' on " + user_date)
    expense.delete()
    return redirect('expenses')

@login_required(login_url='/authentication/login')
def search_expense(request):
    if request.method == "POST":

        # There is a weird bug sometimes it prints duplicate when doing a search for 'WoW' when desc is 'wwwwow'
        query_str = json.loads(request.body).get('searchText', "")
        
        # ex: if query is 1000 then search for amount >1000
        expenses = \
            Expense.objects.filter(amount_spent__istartswith=query_str, owner=request.user) | \
            Expense.objects.filter(date__istartswith=query_str, owner=request.user) | \
            Expense.objects.filter(description__icontains=query_str, owner=request.user) | \
            Expense.objects.filter(category__icontains=query_str, owner=request.user)
        
        data = expenses.values()

        return JsonResponse(list(data), safe = False)

def expense_categories_summary(request):
    curr_date = datetime.date.today()
    six_months_ago = curr_date - datetime.timedelta(days=30*6)
    # Filter for dates < six_months ago but > curr_date
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=curr_date)

    result = {}
    
    def get_category_data(expense):
        return expense.category
    # Map calls the given function for every item in the given list
    # We put  it in a set to remove all the duplicates, because there are multiple instances of categories
    category_list = list(set(map(get_category_data, expenses)))

    def get_expense_category_amount(category):
        # Takes in a category and filters our expenses model for that category
        # and loops over the queryset to retrieve the amount spent for every expense
        amount = 0
        filtered = expenses.filter(category=category)
        for num in filtered:
            amount += num.amount_spent
        return amount

    for x in expenses:
        for y in category_list:
            result[y] = get_expense_category_amount(y)
    
    return JsonResponse({'expense_category_data': result}, safe = False) # Since we know its a list
    
    
def statsView(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'

    csv_writer = csv.writer(resp)
    csv_writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        csv_writer.writerow([expense.amount_spent, expense.description, expense.category, expense.date])
    
    return resp