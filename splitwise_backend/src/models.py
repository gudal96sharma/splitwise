import time
import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings
# Create your models here.

class UserProfileManager(BaseUserManager):
    """ Manager for user profiles """

    def create_user(self, email, name, phone, password=None) -> "UserProfile":
        """Create a new user profile"""
        if not email:
            raise ValueError('Invalid Email')
        # normalize email, convert second half to lowercase
        email = self.normalize_email(email)
        user = self.model(email=email, name=name , phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    """ Database model for users in system """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10,null=True,blank=True)
    is_active = models.BooleanField(default=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone']

    def get_full_name(self) -> str:
        """
        Retrieve full name of user
        :return: str
        """
        return self.name

    def get_short_name(self) -> str:
        """
        Retrieve full name of user
        :return: str
        """
        return self.name

    def __str__(self) -> str:
        """
        Return String representation of User
        :return: str
        """
        return f"Email: {self.email}, Name:{self.name}"

class Debt(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='to_user')
    amount = models.FloatField()

    def __str__(self):
        return f'{self.to_user.name} owes {"%.2f" %self.amount} to {self.from_user.name}'


class Group(models.Model):
    group_name = models.CharField(max_length=255, unique=True)
    debts = models.ManyToManyField(Debt, null=True)
    members = models.ManyToManyField(UserProfile)


class ExpenseUser(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    paid_share = models.IntegerField(default=0)
    owed_share = models.IntegerField(default=0)
    net_balance = models.IntegerField(default=0)

class Expense(models.Model):
    name = models.CharField(max_length=255, unique=True)
    expense_group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True, db_constraint=False)
    description = models.CharField(max_length=255)
    payment = models.BooleanField(default=False)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    repayments = models.ManyToManyField(Debt)
    users = models.ManyToManyField(ExpenseUser)
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

