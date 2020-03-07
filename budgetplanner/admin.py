from django.contrib import admin
from budgetplanner.models import (
    BudgetPlan, CategoryType, Category, Transaction)

admin.site.register(BudgetPlan)
admin.site.register(CategoryType)
admin.site.register(Category)
admin.site.register(Transaction)
