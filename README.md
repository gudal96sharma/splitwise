# splitwise
-> Clone the project using below command:-
   git clone https://github.com/gudal96sharma/splitwise.git
   
-> Download python using below link:-
   https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
   
-> Please install all dependency using below command:-
   pip install -r requirements.txt
   
-> Make changes in settings.py file (Database,Email id and password)

-> Run Makemigration and Migration using below commands:-
   python manage.py makemigrations
   python manage.py migrate
   
-> Run Python Project using below command:-
   python manage.py runserver

# Architecture Diagram:

                             +----------------------+
                             |     Splitwise API    |
                             +----------+-----------+
                                        |
                                        v
                      +-----------------------------+
                      |       Django Backend       |
                      | (Models, Views, Serializers)|
                      +--------------+--------------+
                                     |
                  +------------------+------------------+
                  |                   |                  |
         +--------v-----+    +--------v-----+    +-------v-------+
         |   User API   |    |  Group API   |    | Expense API   |
         |              |    |              |    |               |  
         +--------------+    +--------------+    +--------------+  

# Class Structure:

-> UserProfileManager: Manages user profiles, including creation.

-> UserProfile (User): Represents user profiles with email, name, phone, and activation status.

-> Debt: Tracks debts between users, including the amount owed from one user to another.

-> Group: Represents a group of users, including the group name, debts within the group, and group members.

-> ExpenseUser: Represents users involved in an expense, including their paid share, owed share, and net balance.

-> Expense: Represents an expense, including the name, group it belongs to, description, amount, date, repayments, users involved, and transaction ID.

