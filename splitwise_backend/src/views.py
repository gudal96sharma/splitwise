from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from src import serializers, models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

# Create your views here.

def send_expense_notification_email(user_email, expense_name, amount_owed):
    subject = 'Expense Notification'
    html_message = render_to_string('expense_notification_email.html', {'expense_name': expense_name, 'amount_owed': amount_owed})
    plain_message = ''
    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [user_email], html_message=html_message)

class UserProfileApiView(APIView):
    """Test API View"""
    serializer_class = serializers.UserProfileSerializer

    def post(self, request) -> Response:
        """Create a hello message with our name"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            name = serializer.validated_data.get('name')
            return Response({'message': f'User {name} created successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateGroupApiView(APIView):
    """Group Creation View"""
    serializer_class = serializers.GroupSerializer

    def post(self, request) -> Response:
        all_users = []
        for user_email in request.data.get('members', []):
            all_users.append(models.UserProfile.objects.get(email=user_email).id)
        request.data['members'] = all_users
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Group {serializer.data.get("group_name")} Created successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateExpenseApiView(APIView):
    """Expense Creation View"""
    serializer_class = serializers.ExpenseSerializer

    def post(self, request) -> Response:
        description = request.data.get('description')
        all_users_emails = request.data.get('users')
        all_users = models.UserProfile.objects.filter(email__in=all_users_emails)
        paid_by_email = request.data.get('paid_by')
        paid_by_user = models.UserProfile.objects.get(email=paid_by_email)
        amount = request.data.get('amount')
        group_name = request.data.get('group_name', None)
        expense_name = request.data.get('expense_name')
        split_type = request.data.get('split_type')

        # Ensure the expense name is unique
        if models.Expense.objects.filter(name=expense_name).exists():
            return Response({"message": "Expense name should be unique"}, status=status.HTTP_400_BAD_REQUEST)
        group = None
        if group_name is not None:
            group = models.Group.objects.get(group_name=group_name)
        if split_type == 'EQUAL':
            # Equal Split
            per_member_share = amount / len(all_users)
            repayments = []
            for user in all_users:
                if user != paid_by_user:
                    debt = models.Debt.objects.create(from_user=paid_by_user, to_user=user, amount=per_member_share)
                    repayments.append(debt)
            expense_users = []
            for user in all_users:
                expense_user_dict = {
                    "user": user,
                    "paid_share": per_member_share if user == paid_by_user else 0,
                    "owed_share": per_member_share,
                    "net_balance": per_member_share if user == paid_by_user else -per_member_share
                }
                expense_user = models.ExpenseUser.objects.create(**expense_user_dict)
                expense_users.append(expense_user)
                send_expense_notification_email(user.email, expense_name, per_member_share)


        elif split_type == 'PERCENTAGE':
            # Percentage Split
            percentages = request.data.get('split_values')
            total_percentage = sum(percentages)
            if total_percentage != 100:
                return Response({"message": "Total percentage should be 100"}, status=status.HTTP_400_BAD_REQUEST)
            amounts = [amount * p / 100 for p in percentages]
            repayments = []
            expense_users = []
            for i, user in enumerate(all_users):
                if user != paid_by_user:
                    debt = models.Debt.objects.create(from_user=paid_by_user, to_user=user, amount=amounts[i])
                    repayments.append(debt)
                expense_user_dict = {
                    "user": user,
                    "paid_share": amounts[i] if user == paid_by_user else 0,
                    "owed_share": amounts[i],
                    "net_balance": amounts[i] if user == paid_by_user else -amounts[i]
                }
                expense_user = models.ExpenseUser.objects.create(**expense_user_dict)
                expense_users.append(expense_user)
                send_expense_notification_email(user.email, expense_name, amounts[i])

        elif split_type == 'EXACT':
            # Exact Split
            exact_amounts = request.data.get('split_values')
            if len(exact_amounts) != len(all_users):
                return Response({"message": "Number of amounts does not match the number of users"}, status=status.HTTP_400_BAD_REQUEST)
            total_amount = sum(exact_amounts)
            if total_amount != amount:
                return Response({"message": "Total amount does not match the sum of exact amounts"}, status=status.HTTP_400_BAD_REQUEST)
            repayments = []
            expense_users = []
            for i, user in enumerate(all_users):
                if user != paid_by_user:
                    debt = models.Debt.objects.create(from_user=paid_by_user, to_user=user, amount=exact_amounts[i])
                    repayments.append(debt)
                expense_user_dict = {
                    "user": user,
                    "paid_share": exact_amounts[i] if user == paid_by_user else 0,
                    "owed_share": exact_amounts[i],
                    "net_balance": exact_amounts[i] if user == paid_by_user else -exact_amounts[i]
                }
                expense_user = models.ExpenseUser.objects.create(**expense_user_dict)
                expense_users.append(expense_user)
                send_expense_notification_email(user.email, expense_name, exact_amounts[i])

        elif split_type == 'SHARE':
            # Split by Share
            shares = request.data.get('split_values')
            total_shares = sum(shares)
            amounts = [amount * s / total_shares for s in shares]
            repayments = []
            expense_users = []
            for i, user in enumerate(all_users):
                if user != paid_by_user:
                    debt = models.Debt.objects.create(from_user=paid_by_user, to_user=user, amount=amounts[i])
                    repayments.append(debt)
                expense_user_dict = {
                    "user": user,
                    "paid_share": amounts[i] if user == paid_by_user else 0,
                    "owed_share": amounts[i],
                    "net_balance": amounts[i] if user == paid_by_user else -amounts[i]
                }
                expense_user = models.ExpenseUser.objects.create(**expense_user_dict)
                expense_users.append(expense_user)
                send_expense_notification_email(user.email, expense_name, amounts[i])

        else:
            return Response({"message": "Invalid split type"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the expense
        expense = models.Expense.objects.create(
            expense_group=group,
            description=description,
            amount=amount,
            name=expense_name
        )
        expense.repayments.set(repayments)
        expense.users.set(expense_users)
        return Response({'message': 'Expense created successfully'})

class ShowGroupExpenseDetailsApiView(APIView):
    def get(self, request) -> Response:
        group_name = request.GET['group_name']
        try:
            group = models.Group.objects.get(group_name=group_name)
            expenses = models.Expense.objects.filter(expense_group=group, payment=False)
            data = list()
            for expense in expenses:
                exp = {
                    "name": expense.name,
                    "Description": expense.description,
                    "repayments": [str(x) for x in expense.repayments.all() if
                                   x.from_user != x.to_user and x.amount != 0]
                }
                data.append(exp)
            return Response(
                {'message': data
                 }
            )
        except models.Group.DoesNotExist:
            return Response(
                {'message': 'Group Does not exist !'
                 },
                status=status.HTTP_404_NOT_FOUND
            )

class ShowUserDetailsApiView(APIView):
    """Show user details"""

    def get(self, request) -> Response:
        user_email = request.GET['email']
        try:
            user = models.UserProfile.objects.get(email=user_email)
            f_debts = models.Debt.objects.filter(from_user=user)
            t_debts = models.Debt.objects.filter(to_user=user)
            debt_data = dict()
            debit = 0
            credit = 0
            for i in f_debts:
                debt_data[i.to_user.name] = debt_data.get(i.to_user.name, 0) - i.amount
                debit -= i.amount
            for i in t_debts:
                debt_data[i.from_user.name] = debt_data.get(i.from_user.name, 0) + i.amount
                credit += i.amount
            return Response(
                {'message':
                    {
                        'user': f'{user}',
                        'debit': "%.2f" %debit,
                        'credit': "%.2f" %credit,
                        'data': [f'User {user.name} ows {"%.2f" %debt_data[x]} to user {x}' if debt_data[x] > 0 else f'User {user.name} owes {"%.2f" % (-1 * debt_data[x])} to {x}'
                                 for x in debt_data if
                                 x != user.name and debt_data[x] != 0],
                    }
                }
            )
        except models.UserProfile.DoesNotExist:
            return Response(
                {'message': 'User Does not exist !'
                 },
                status=status.HTTP_404_NOT_FOUND
            )
