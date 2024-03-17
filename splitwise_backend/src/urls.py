from django.urls import path, include
from .views import *

urlpatterns = [
    path('createuser', UserProfileApiView.as_view()),
    path('creategroup', CreateGroupApiView.as_view()),
    path('addexpense', CreateExpenseApiView.as_view()),
    path('groupexpense', ShowGroupExpenseDetailsApiView.as_view()),
    path('userexpensedetails', ShowUserDetailsApiView.as_view()),
    ]
