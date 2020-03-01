from django.db import models
from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class CategoryType(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    cat_type = models.ForeignKey(CategoryType, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='categories')
    amount_planned = models.FloatField(default=0)
    description = models.TextField(default='', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.user.username + ' - ' + self.name.capitalize()


class Transaction(models.Model):
    date = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='transaction')
    amount = models.FloatField()
    description = models.CharField(max_length=100)
    comment = models.TextField(null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description[:10]
