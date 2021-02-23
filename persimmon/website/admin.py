from django.contrib import admin  # pylint: disable=unused-import

from .models import User, BankAccount, BankStatements

# Register your models here.
admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(BankStatements)
