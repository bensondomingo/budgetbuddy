from pprint import pprint

from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse

from django.conf import settings

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from budgetplanner.api.serializers import CategoryTypeSerializer
from budgetplanner.api.serializers import CategorySerializer
from budgetplanner.models import CategoryType, Category


USER_MODEL = get_user_model()
ADMIN_USERNAME = settings.ADMIN_USERNAME
DEFAULT_CATEGORY_TYPES = settings.BUDGET_PLANNER_DEFAULTS['CATEGORY_TYPES']
DEFAULT_CATEGORIES = settings.BUDGET_PLANNER_DEFAULTS['CATEGORIES']


class BudgetPlannerEndpointTestCase(APITestCase):

    admin_creds = {'username': ADMIN_USERNAME,
                   'email': f'{ADMIN_USERNAME}@budgetbuddy.com',
                   'password': 'test1234'}
    usera_creds = {'username': 'usera',
                   'email': 'usera@gmail.com', 'password': 'test1234'}
    userb_creds = {'username': 'userb',
                   'email': 'userb@gmail.com', 'password': 'test1234'}

    def _create_user(self, username, email, password, superuser=False):
        if not superuser:
            user = USER_MODEL.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            # Create a token for this user
            Token.objects.create(user=user)
        else:
            user = USER_MODEL.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            # Create a token for this user
            Token.objects.create(user=user)

        return user

    def _login_user(self, username):
        user = USER_MODEL.objects.get(username=username)
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def _logout_user(self):
        self.client.logout()

    @classmethod
    def setUpClass(cls):
        '''
        Test Setup: Create admin and common user on the database
        '''
        # admin
        user = USER_MODEL.objects.create_superuser(**cls.admin_creds)
        # Create a token for this user
        Token.objects.create(user=user)

    @classmethod
    def tearDownClass(cls):
        user = USER_MODEL.objects.get(username=cls.admin_creds['username'])
        user.delete()

    def setUp(self):
        '''
        Create objects
        '''
        # Login admin and create default category types
        self._login_user(self.admin_creds['username'])
        # response = self.client.post(path=reverse('create-defaults'))
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(len(response.data), 3)

        # create users
        self._create_user(**self.usera_creds)
        usera = USER_MODEL.objects.get(username=self.usera_creds['username'])
        self._create_user(**self.userb_creds)
        userb = USER_MODEL.objects.get(username=self.userb_creds['username'])

        # create category type per user
        CategoryType.objects.create(name='usera_test_cat_type', user=usera)
        CategoryType.objects.create(name='userb_test_cat_type', user=userb)


class CategoryTypeEndpointTestCase(BudgetPlannerEndpointTestCase):

    list_endpoint = 'category-type-list'
    detail_endpoint = 'category-type-detail'

    def test_list_cat_type(self):
        '''
        Test list endpoint.
        '''
        usera_test_cat_type = CategoryType.objects.get(
            name='usera_test_cat_type')
        userb_test_cat_type = CategoryType.objects.get(
            name='userb_test_cat_type')
        usera_test_cat_type = CategoryTypeSerializer(usera_test_cat_type)
        userb_test_cat_type = CategoryTypeSerializer(userb_test_cat_type)

        # usera
        self._login_user(self.usera_creds['username'])
        response = self.client.get(path=reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect 4 items. 3 created by admin, 1 created by user
        self.assertEqual(len(response.data), 4)
        self.assertIn(usera_test_cat_type.data, response.data)
        # Test if object created by userb is not available for usera
        self.assertNotIn(userb_test_cat_type.data, response.data)
        self._logout_user()

        # userb
        self._login_user(self.userb_creds['username'])
        response = self.client.get(path=reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect 4 items. 3 created by admin, 1 created by user
        self.assertEqual(len(response.data), 4)
        self.assertNotIn(usera_test_cat_type.data, response.data)

        self.assertIn(userb_test_cat_type.data, response.data)
        self._logout_user()

        # anonymous user
        # API requires user to login to access list endpoint.
        # GETing on this endpoint will raise HTTP_401_UNAUTHORIZED
        response = self.client.get(path=reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_cat_type(self):
        '''
        Create common category type for usera and userb. The API allows
        duplicate CategoryType.name as long it was created by different
        users.
        '''

        # usera
        self._login_user(self.usera_creds['username'])
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'user_test_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # create duplicate category type for usera. This should result in
        # HTTP_400_BAD_REQUEST.
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'user_test_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self._logout_user()

        # userb
        self._login_user(self.userb_creds['username'])
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'user_test_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # create duplicate category type for userb. This should result in
        # HTTP_400_BAD_REQUEST.
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'user_test_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self._logout_user()

        # anonymous user
        # API requires user to login to access create endpoint.
        # POSTing on this endpoint will raise HTTP_401_UNAUTHORIZED
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'user_test_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_cat_type(self):
        usera_test_cat_type = CategoryType.objects.get(
            name='usera_test_cat_type')
        userb_test_cat_type = CategoryType.objects.get(
            name='userb_test_cat_type')
        usera_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': usera_test_cat_type.id})
        userb_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': userb_test_cat_type.id})

        # usera
        self._login_user(self.usera_creds['username'])
        # test update own object
        response = self.client.put(
            usera_endpoint, data={'name': 'usera_up_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # verify object updated
        response = self.client.get(usera_endpoint)
        name = response.data.get('name')
        self.assertEqual(name, 'usera_up_cat_type')
        # test update unowned object
        response = self.client.put(userb_endpoint, data={
                                   'name': 'usera_up_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self._logout_user()

        # userb
        self._login_user(self.userb_creds['username'])
        # test update own object
        response = self.client.put(
            userb_endpoint, data={'name': 'userb_up_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # verify object updated
        response = self.client.get(userb_endpoint)
        name = response.data.get('name')
        self.assertEqual(name, 'userb_up_cat_type')
        # test update unowned object
        response = self.client.put(usera_endpoint, data={
                                   'name': 'userb_up_cat_type'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # rename category type object so that it will conflict with another
        # object's name. The API should prevent this action.

        # First create a new category type called "test"
        response = self.client.post(path=reverse(self.list_endpoint), data={
                                    'name': 'test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Now update "userb_up_cat_type" name to "test". This should result to
        # HTTP_400_BAD_REQUEST
        response = self.client.put(
            userb_endpoint, data={'name': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.json()), 1)
        error_msg = response.data.get('name')
        self.assertIn('exist', *error_msg)
        self._logout_user()

    def test_destroy_cat_type(self):
        usera_test_cat_type = CategoryType.objects.get(
            name='usera_test_cat_type')
        userb_test_cat_type = CategoryType.objects.get(
            name='userb_test_cat_type')
        usera_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': usera_test_cat_type.id})
        userb_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': userb_test_cat_type.id})

        default_cat_type = CategoryType.objects.get(name='income')

        # usera
        self._login_user(self.usera_creds['username'])
        response = self.client.delete(usera_endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(usera_endpoint)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # test delete unowned object
        response = self.client.delete(userb_endpoint)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # test delete default object
        response = self.client.delete(
            reverse(self.detail_endpoint, kwargs={'pk': default_cat_type.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CategoryEnpointTestCase(BudgetPlannerEndpointTestCase):

    list_endpoint = 'category-list'
    detail_endpoint = 'category-detail'

    def setUp(self):
        super().setUp()

        # Create new categories
        usera = USER_MODEL.objects.get(username=self.usera_creds['username'])
        userb = USER_MODEL.objects.get(username=self.userb_creds['username'])
        income = CategoryType.objects.get(name='income')
        expenditure = CategoryType.objects.get(name='expenditure')

        Category.objects.create(
            name='usera_test_income_category',
            amount_planned='10000', user=usera, cat_type=income)
        Category.objects.create(
            name='usera_test_expenditure_category',
            amount_planned='5000',
            user=usera, cat_type=expenditure)
        Category.objects.create(
            name='userb_test_income_category',
            amount_planned='10000', user=userb, cat_type=income)
        Category.objects.create(
            name='userb_test_expenditure_category',
            amount_planned='5000',
            user=userb, cat_type=expenditure)

    def test_list_cat_endpoint(self):
        # verify default categories were created
        self._login_user(self.usera_creds['username'])
        response = self.client.get(reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for category in DEFAULT_CATEGORIES:
            name = category.get('name')
            category = next(
                item for item in response.data if item['name'] == name)
            self.assertNotEqual(category, None)

        _len = len(Category.objects.filter(
            user__username=self.usera_creds['username']))
        self.assertEqual(len(response.data), _len)
        self._logout_user()

        self._login_user(self.userb_creds['username'])
        response = self.client.get(reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = [category for category in response.data
                      if category.get('user') == self.userb_creds['username']]
        self.assertEqual(len(categories), 12)
        self._logout_user()

        # test searching
        self._login_user(self.usera_creds['username'])
        response = self.client.get(
            reverse(self.list_endpoint) + '?search=income')
        self.assertEqual(len(response.data), 1)
        response = self.client.get(
            reverse(self.list_endpoint) + '?search=userb_test_income_category')
        self.assertEqual(len(response.data), 0)

        # test ordering
        response = self.client.get(
            reverse(self.list_endpoint) + '?ordering=-amount_planned')
        data = iter(response.data)
        self.assertEqual(next(data).get('name'), 'usera_test_income_category')
        self.assertEqual(next(data).get('name'),
                         'usera_test_expenditure_category')
        self._logout_user()

        # test anonymous user
        response = self.client.get(reverse(self.list_endpoint))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_cat_endpoint(self):
        income = CategoryType.objects.get(name='income')
        expenditure = CategoryType.objects.get(name='expenditure')

        # usera
        self._login_user(self.usera_creds['username'])
        response = self.client.post(reverse(self.list_endpoint), data={
                                    'name': 'usera_test_income_category_2',
                                    'cat_type': income.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse(self.list_endpoint), data={
                                    'name': 'usera_test_expenditure_category_2',
                                    'cat_type': expenditure.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test duplicate
        response = self.client.post(reverse(self.list_endpoint), data={
                                    'name': 'usera_test_income_category_2',
                                    'cat_type': income.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self._logout_user()

        # test anonymous
        response = self.client.post(reverse(self.list_endpoint), data={
                                    'name': 'anonymous_test_income_category',
                                    'cat_type': income.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_cat_endpoint(self):

        # usera
        self._login_user(self.usera_creds['username'])
        response = self.client.get(
            reverse(self.list_endpoint) + '?search=income')
        data = response.json()[0]
        usera_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': data.get('id')})
        data['amount_planned'] = 20000
        response = self.client.put(usera_endpoint, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('amount_planned'), 20000)

        # rename a category object so that it will conflict with another
        # object's name. The API should prevent this action.

        # First create a new category object
        expenditure = CategoryType.objects.get(name='expenditure')
        response = self.client.post(
            reverse(self.list_endpoint),
            data={'name': 'test', 'cat_type': expenditure.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Then rename it so that it will conflict with an existing
        # category object i.e food category
        data = response.data
        usera_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': data.get('id')})
        data['name'] = 'food'
        response = self.client.put(usera_endpoint, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        error_msg = response.data.get('name')
        self.assertIn('exist', *error_msg)

        self._logout_user()

        # test anonymous user
        response = self.client.put(usera_endpoint, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_cat_endpoint(self):
        category = Category.objects.get(name='usera_test_expenditure_category')

        self._login_user(self.usera_creds['username'])
        usera_endpoint = reverse(self.detail_endpoint, kwargs={
                                 'pk': category.id})
        response = self.client.get(usera_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # perform DELETE request
        response = self.client.delete(usera_endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(usera_endpoint)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_null_with_cat_type(self):
        test_cat_type = CategoryType.objects.get(name='usera_test_cat_type')
        # create a new category and set test_cat_type as cat_type
        category = Category.objects.create(name='test', cat_type=test_cat_type)
        self.assertEqual(category.cat_type.id, test_cat_type.id)

        # delete test_cat_type
        test_cat_type.delete()
        category = Category.objects.get(name='test')
        self.assertEqual(category.cat_type, None)
