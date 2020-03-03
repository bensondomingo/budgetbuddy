from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from profiles.models import Profile
from budgetplanner.models import CategoryType, Category


USER_MODEL = get_user_model()
ADMIN_USERNAME = settings.ADMIN_USERNAME
DEFAULT_CATEGORY_TYPES = settings.BUDGET_PLANNER_DEFAULTS['CATEGORY_TYPES']
DEFAULT_CATEGORIES = settings.BUDGET_PLANNER_DEFAULTS['CATEGORIES']


@receiver(post_save, sender=USER_MODEL)
def create_default_category(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser and instance.username == ADMIN_USERNAME:
            admin = USER_MODEL.objects.get(username=ADMIN_USERNAME)
            for category_type in DEFAULT_CATEGORY_TYPES:
                CategoryType.objects.create(name=category_type, user=admin)

        else:
            # Create default expenditure categories
            expenditure = CategoryType.objects.get(name='expenditure')

            for category in DEFAULT_CATEGORIES:
                Category.objects.create(
                    name=category.get('name'),
                    user=instance,
                    category_type=expenditure,
                    description=category.get('description')
                )
