from django.db import models
from django.apps import apps
from django.utils.translation import gettext as _


class AddressBook(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    origin_google_account = models.ForeignKey("GoogleAccount", null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    origin_internal_addressbook = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
        #limit_choices_to={
        #    'origin_google_account__isnull': True
        #}
    )
    origin_radicale_account = models.ForeignKey("RadicaleAccount", null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    export_radicale_account = models.ForeignKey("RadicaleAccount", null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    export_filter_groups = models.ManyToManyField("PersonGroup", blank=True)

    @property
    def origin_account(self):
        return self.origin_google_account or self.origin_internal_addressbook or self.origin_radicale_account or self

    @property
    def destination_account(self):
        return self.export_radicale_account

    def __str__(self):
        if self.destination_account:
            return f'{self.title}: {self.origin_account.account_type} -> {self.destination_account.account_type}'
        return f'{self.title}: {self.origin_account.account_type} -> {self.account_type}'

    @property
    def account_type(self):
        return 'Internal'

    def get_persons(self):
        account = apps.get_model('django_contacts.Account').objects.filter(google_account=self.origin_google_account).first()
        return apps.get_model('django_contacts.Person').objects.filter(account=account)
