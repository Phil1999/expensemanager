from django.contrib import admin
from .models import Expense, Category
# Register your models here.




class ExpenseAdmin(admin.ModelAdmin):
    # Adding search and more attributes to expenses page of admin
    list_display = ('amount_spent', 'description', 'owner', 'category', 'date',)
    search_fields = ('description', 'category', 'date',)

    list_per_page = 5

admin.site.register(Category)
admin.site.register(Expense, ExpenseAdmin)