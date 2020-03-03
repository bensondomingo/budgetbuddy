from django.db.models import Q
from django.conf import settings

from rest_framework import serializers

from budgetplanner.models import Category, CategoryType, Transaction


ADMIN_USERNAME = settings.ADMIN_USERNAME


class CategoryTypeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    # categories = CategorySerializer(
    #     source='category', many=True, read_only=True)

    class Meta:
        model = CategoryType
        fields = '__all__'

    def validate_name(self, value):
        user = self.context['request'].user
        category_types = CategoryType.objects.filter(
            Q(user__username=ADMIN_USERNAME) | Q(user=user))

        try:
            category_type = category_types.get(name=value)
        except CategoryType.DoesNotExist:
            return value
        else:
            if self.context['request'].method == 'POST':
                raise serializers.ValidationError(
                    f'{value} category type already exist')

            else:   # PUT or PATCH
                if category_type.id != self.instance.id:
                    raise serializers.ValidationError(
                        f'{value} category type already exist')
            return value


class CategorySerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()
    amount_actual = serializers.SerializerMethodField()
    amount_left = serializers.SerializerMethodField()
    category_type = serializers.CharField(
        source='category_type.name', read_only=True)
    category_type_id = serializers.IntegerField(
        source='category_type.id', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        try:
            category = Category.objects.get(
                user=self.context['request'].user, name=value)
        except Category.DoesNotExist:
            return value
        else:

            if self.context['request'].method == 'POST':
                raise serializers.ValidationError(
                    f'{value} category already exist')

            else:   # PUT or PATCH
                if category.id != self.instance.id:
                    raise serializers.ValidationError(
                        f'{value} category already exist')
            return value

    def get_amount_actual(self, obj):
        return sum([transaction.amount for transaction in obj.transactions.all()])

    def get_amount_left(self, obj):
        return obj.amount_planned - self.get_amount_actual(obj)


class TransactionSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        read_only=True, source='category.name')
    user = serializers.CharField(read_only=True, source='user.username')

    class Meta:
        model = Transaction
        fields = '__all__'
