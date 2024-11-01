from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


class GoogleAccountAdmin(admin.ModelAdmin):
    actions = ['update_token', 'get_10_contacts']
    list_display = ['__str__', 'google_expire_token', 'google_token_expires_in', 'last_api_called', 'token_is_expired']

    def update_token(self, request, queryset):
        for obj in queryset:
            print(f"Token before {obj.token}")
            obj.get_api()
            print(f"Token after {obj.token}")

    def get_10_contacts(self, request, queryset):
        for obj in queryset:
            obj.get_api().get_ten_contacts()


class PersonAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'nickname', 'rendered_first_photo_url']
    search_fields = ['last_name', 'first_name', 'nickname']

    @admin.display(description='Bild', ordering='first_name')
    def rendered_first_photo_url(self, obj):
        return mark_safe(f'<img src="{obj.first_photo_url}" alt="{obj}" style="max-height: 1.3rem;">')


class AddressBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'origin_account', 'destination_account']


class AccountAdmin(admin.ModelAdmin):
    actions = ['import_contacts']

    def import_contacts(self, request, queryset):
        for obj in queryset:
            obj.import_contacts()


class InstantMessangerAdmin(admin.ModelAdmin):
    list_display = ['username', 'im_type', '__str__']


class PersonPhoneConnectionAdmin(admin.ModelAdmin):
    list_display = ['person', 'phone', 'usage']

admin.site.register(models.Phone)
admin.site.register(models.PersonPhoneConnection, PersonPhoneConnectionAdmin)
admin.site.register(models.PersonEmailConnection)
admin.site.register(models.UsageCategory)
admin.site.register(models.Company)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Address)
admin.site.register(models.GoogleAccount, GoogleAccountAdmin)
admin.site.register(models.PersonAddressConnection)
admin.site.register(models.AddressBook, AddressBookAdmin)
admin.site.register(models.RadicaleAccount)
admin.site.register(models.Email)
admin.site.register(models.InstantMessanger, InstantMessangerAdmin)
admin.site.register(models.Account, AccountAdmin)
