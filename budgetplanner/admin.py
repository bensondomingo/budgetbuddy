from django.contrib import admin
from budgetplanner.models import Category, CategoryType, Transaction

admin.site.register(Category)
admin.site.register(CategoryType)
admin.site.register(Transaction)
