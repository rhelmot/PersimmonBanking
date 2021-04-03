from django.contrib import admin  # pylint: disable=unused-import
from .models import User, BankAccount, Appointment, SignInHistory, Transaction, UserEditRequest, TransactionApproval, \
    SignInFailure


def approve_edit_request(modeladmin, request, queryset):  # pylint: disable=unused-argument
    for req in queryset:
        req.apply()
        req.delete()
approve_edit_request.short_description = 'Approve Request'


class UserEditRequestAdmin(admin.ModelAdmin):
    actions = [approve_edit_request]


class SignInHistoryAdmin(admin.ModelAdmin):
    actions = None

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(User)
admin.site.register(BankAccount)
admin.site.register(Transaction)
admin.site.register(Appointment)
admin.site.register(TransactionApproval)
admin.site.register(SignInHistory, SignInHistoryAdmin)
admin.site.register(SignInFailure, SignInHistoryAdmin)
admin.site.register(UserEditRequest, UserEditRequestAdmin)
