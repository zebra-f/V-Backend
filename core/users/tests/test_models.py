from django.test import TestCase
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from core.users.models import User, UserPersonalProfile


class TestUser(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.userone = User.objects.create_user(
            'testuserone@email.com',
            'testuserone',
            '6A37xvby&1!L'
            )
        UserPersonalProfile(user=cls.userone).save()
        cls.usertwo = User.objects.create_user(
            'testusertwo@email.com',
            'testusertwo',
            '6A37xvby&1!L'
        )
        UserPersonalProfile(user=cls.usertwo).save()
        
        cls.user_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
        users = []
        for user_number in cls.user_numbers[2:]:
            users.append(User(
                email=f'testuser{user_number}@email.com', 
                username=f'testuser{user_number}',
                password=User.objects.make_random_password()))
        User.objects.bulk_create(users)
        
        return super().setUpTestData()

    def test_username(self):
        self.assertEqual(self.userone.username, 'testuserone')
        self.assertEqual(self.usertwo.username, 'testusertwo')

    def test_ordering(self):
        '''ordering = ['-created_at']'''
        time_to_compare = timezone.now()
        i = len(self.user_numbers) - 1
        for user in User.objects.all():
            self.assertLessEqual(user.created_at, time_to_compare)
            time_to_compare = user.created_at
            self.assertEqual(user.username[8:], self.user_numbers[i])
            i -= 1

    def test_is_active(self):
        for user in User.objects.all():
            self.assertEqual(user.is_active, False)

    def test_password(self):
        self.assertNotEqual(self.userone.password, make_password('6A37xvby&1!L'))
        self.assertNotEqual(self.usertwo.password, make_password('6A37xvby&1!L'))
        self.assertNotEqual(self.userone.password, self.usertwo.password)
        self.assertEqual(check_password('6A37xvby&1!L', self.userone.password), True)
        self.assertEqual(check_password('6A37xvby&1!L', self.usertwo.password), True)
        self.assertEqual(check_password('5A37xvby&1!L', self.userone.password), False)
        self.assertEqual(check_password('7A37xvby&1!L', self.usertwo.password), False)

    def test_queryset(self):
        self.assertEqual(User.objects.count(), 8)

    def test_fields(self):
        for user in User.objects.all():
            self.assertLessEqual(user.created_at, timezone.now())
            self.assertLessEqual(user.updated_at, timezone.now())
            self.assertEqual(user.last_login, None)
            self.assertEqual(user.last_logout, None)
            self.assertEqual(user.is_staff, False)
    
    def test_retation(self):
        self.assertEqual(self.userone.user_personal_profile.first_name, None)
        self.assertEqual(self.userone.email, self.userone.user_personal_profile.user.email)
        self.assertEqual(self.usertwo.user_personal_profile.first_name, None)
        self.assertEqual(self.usertwo.email, self.usertwo.user_personal_profile.user.email)
