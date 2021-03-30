from django.contrib import admin  # pylint: disable=unused-import
from .models import User, BankAccount, Appointment, SignInHistory, Transaction, UserEditRequest


def approve_edit_request(modeladmin, request, queryset):  # pylint: disable=unused-argument
    for req in queryset:
        req.apply()
        req.delete()
approve_edit_request.short_description = 'Approve Request'


class UserEditRequestAdmin(admin.ModelAdmin):
    actions = [approve_edit_request]


# Register your models here.
admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(Appointment)
admin.site.register(SignInHistory)
admin.site.register(Transaction)
admin.site.register(UserEditRequest, UserEditRequestAdmin)
