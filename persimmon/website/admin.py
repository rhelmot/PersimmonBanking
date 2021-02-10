from django.contrib import admin  # pylint: disable=unused-import

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(BankStatements)
admin.site.register(Appointment)
