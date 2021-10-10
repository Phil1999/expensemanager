from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name = "expenses"),
    path('add-expense', views.add_expense, name = 'add-expense'),
    path('edit-expense/<int:id>', views.edit_expense, name = 'edit-expense'),
    path('delete-expense/<int:id>', views.delete_expense, name = 'delete-expense'),
    path('search-expense', csrf_exempt(views.search_expense), name = 'search-expense'),
    path('expense_categories_summary', views.expense_categories_summary, name = 'expense_categories_summary'),
    path('stats', views.statsView, name= "stats"),
    path('export_csv', views.export_csv, name= "export-csv"),
    
]