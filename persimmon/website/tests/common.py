from ..models import EmployeeLevel
from ..views import create_user_account

create_user_account(username="test_username",
                    first_name='Firstname',
                    last_name='Lastname',
                    password='password',
                    email='example@example.com',
                    phone='0000000000',
                    address='nowhere',
                    employee_level=EmployeeLevel.CUSTOMER)
