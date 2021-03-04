from django.contrib import admin  # pylint: disable=unused-import
from .models import User, BankAccount, Appointment, SignInHistory

# Register your models here.
admin.site.register(Appointment)
admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(Appointment)
admin.site.register(SignInHistory)
