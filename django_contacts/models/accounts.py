from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.timesince import timeuntil

from django.utils.translation import gettext as _
from ..models.person import Person


class Account(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    google_account = models.ForeignKey('GoogleAccount', null=True, blank=True, on_delete=models.CASCADE)
    radicale_account = models.ForeignKey('RadicaleAccount', null=True, blank=True, on_delete=models.CASCADE)

    @property
    def accounts(self):
        return [
            self.google_account,
            self.radicale_account
        ]

    @property
    def set_accounts(self):
        return [a for a in self.accounts if a is not None]

    @property
    def rel_account(self):
        account = next((account for account in self.accounts if account is not None), None)
        return account

    def clean(self):
        if len(self.set_accounts) > 1:
            raise ValidationError(_('Select only one account'))
        if len(self.set_accounts) == 0:
            raise ValidationError(_('Select one Account'))

    def __str__(self):
        return f'{self.user}@{self.rel_account}'

    def import_contacts(self):
        self.rel_account.import_contacts(account=self)


class GoogleAccount(models.Model):
    credentials = models.JSONField()
    token = models.JSONField(null=True, blank=True)
    last_api_called = models.DateTimeField(null=True, blank=True)
    api_call_counter = models.PositiveIntegerField(default=0)

    def get_api(self):
        from django_contacts.connectors.google import GoogleContactAPI
        api = GoogleContactAPI(credentials=self.credentials, token=self.token)
        api.get_service()
        self.token = api.token
        self.last_api_called = timezone.now()
        self.api_call_counter += 1
        self.save()
        return api

    def import_contacts(self, account):
        return self.import_google_contacts(account=account)

    def import_google_contacts(self, account: Account):
        #ten_contacts = self.get_api().get_ten_contacts()
        ten_contacts = self.get_api().get_all_contacts()
        from ..models import person as person_mdls
        from ..models import person_connections as person_con_mdls
        if ten_contacts:
            for cd in ten_contacts:
                try:
                    first_name = None
                    last_name = None
                    nickname = None
                    for nd in cd.get('names', []):
                        first_name = nd.get('givenName')
                        last_name = nd.get('familyName')
                        if first_name or last_name:
                            break
                    for nn in cd.get('nicknames', []):
                        nickname = nn.get('value')
                        if nickname:
                            break
                    if nickname:
                        print("nickname", nickname, cd)

                    photo_url = cd['photos'][0]['url']
                    resource_name = cd['resourceName']

                    person = None

                    base_person_filters = {
                        'account': account
                    }

                    person_qs = Person.objects.filter(
                        google_resource_name=resource_name,
                        **base_person_filters
                    )

                    if person_qs.count() == 1:
                        person = person_qs.get()
                    else:
                        if last_name and not first_name:
                            person_qs = Person.objects.filter(
                                first_name__isnull=True,
                                last_name=last_name,
                                **base_person_filters
                            )
                        if first_name and not last_name:
                            person_qs = Person.objects.filter(
                                first_name=first_name,
                                last_name__isnull=True,
                                **base_person_filters
                            )
                        if last_name and first_name:
                            person_qs = Person.objects.filter(
                                first_name=first_name,
                                last_name=last_name,
                                **base_person_filters
                            )
                        if nickname:
                            person_qs = Person.objects.filter(
                                nickname=nickname,
                                **base_person_filters
                            )

                    if person_qs.count() == 1:
                        person = person_qs.get()

                    if not person:
                        print("Creating", first_name, last_name, photo_url)

                        person = Person(
                            first_name=first_name,
                            last_name=last_name,
                            nickname=nickname,
                            photo_url=photo_url,
                            google_resource_name=resource_name,
                            **base_person_filters
                        )
                        person.save()

                    phone_numbers = cd.get('phoneNumbers', [])
                    for pn in phone_numbers:
                        pn_nr = pn.get('canonicalForm')
                        pn_type = pn.get('type')
                        pn_ftype = pn.get('formattedType')
                        # fallback
                        if not pn_nr:
                            pn_nr = pn.get('value')

                        usage_cat, usage_cat_created = person_mdls.UsageCategory.objects.get_or_create(
                            text=pn_ftype or pn_type or "unknown"
                        )

                        if pn_nr:
                            pn_obj, pn_obj_created = person_mdls.Phone.objects.get_or_create(phone_number=pn_nr)
                            pn_per_con, pn_per_con_created = person_con_mdls.PersonPhoneConnection.objects.get_or_create(
                                person=person, phone=pn_obj, defaults={'usage': usage_cat}
                            )

                    memberships = cd.get('memberships', [])  # {'contactGroupMembership': {'contactGroupId': 'myContacts', ...}}
                    organizations = cd.get('organizations', [])  # {'name': 'KBS Infra München', 'title': 'BayWa Polier'}
                    emailAddresses = cd.get('emailAddresses', [])  # {'value': 'c@c.de', 'type': 'home', 'formattedType'}
                    birthdays = cd.get('birthdays', [])  # {'date': {'year': 1984, 'month': 6, 'day': 21}
                    imClients = cd.get('imClients', [])  # 'username': 'xxx', 'type': 'other', 'formattedType': 'Other', 'protocol': 'skype', 'formattedProtocol': 'Skype'}

                    for org in organizations:
                        # sometimes only title given, and no company name
                        org_name = org.get('name')
                        if org_name:
                            comp_obj, comp_obj_created = person_mdls.Company.objects.get_or_create(name=org_name)
                            person_com_title = org.get('title')
                            person_com_obj, person_com_obj_created = person_con_mdls.PersonCompanyConnection.objects.get_or_create(person=person, company=comp_obj, defaults={'title': person_com_title})
                            if person_com_title != person_com_obj.title:
                                person_com_obj.title = person_com_title
                                person_com_obj.save()

                    for im in imClients:
                        im_username = im.get('username')
                        im_type = im.get('protocol')
                        person_im, person_im_created = person_mdls.InstantMessanger.objects.get_or_create(username=im_username, im_type=im_type)
                        person_im_con, person_im_con_created = person_con_mdls.PersonIMConnection.objects.get_or_create(person=person, im=person_im)

                    for email in emailAddresses:
                        person_email, person_email_created = person_mdls.Email.objects.get_or_create(email=email.get('value'))
                        email_usage_cat, email_usage_cat_created = person_mdls.UsageCategory.objects.get_or_create(
                            text=email.get('formattedType') or email.get('type') or "unknown"
                        )
                        person_email_con, person_email_con_created = person_con_mdls.PersonEmailConnection.objects.get_or_create(
                            person=person,
                            email=person_email,
                            defaults={'usage': email_usage_cat}
                        )
                        if person_email_con.usage != email_usage_cat:
                            person_email_con.usage = email_usage_cat
                            person_email_con.save()

                    for bd in birthdays:
                        bd_yr = bd['date'].get('year')
                        bd_mn = bd['date'].get('month')
                        bd_d = bd['date'].get('day')
                        if bd_yr is not None and bd_mn is not None and bd_d is not None:
                            date_obj = timezone.datetime(bd_yr, bd_mn, bd_d)
                            person.birthday = date_obj

                    # finally update person and save
                    person.nickname = nickname
                    person.first_name = first_name
                    person.last_name = last_name
                    person.photo_url = photo_url
                    person.save()

                except KeyError as err:
                    print(err)
                    print(cd)

    @property
    def google_project_id(self):
        return self.credentials.get('installed', {}).get('project_id')

    @property
    def google_expire_token(self):
        if self.token:
            expiry = self.token.get('expiry')
            if expiry:
                dt = datetime.strptime(
                    expiry.rstrip("Z").split(".")[0], "%Y-%m-%dT%H:%M:%S"
                )
                aware = timezone.make_aware(dt, timezone=timezone.get_current_timezone())
                return aware

    @property
    def token_is_expired(self):
        return self.google_expire_token < timezone.now()

    @property
    def google_token_expires_in(self):
        expires_dt = self.google_expire_token
        if expires_dt:
            return timeuntil(expires_dt)

    def __str__(self):
        return f'google://{self.google_project_id}'

    @property
    def account_type(self):
        return 'Google'


class RadicaleAccount(models.Model):
    host = models.CharField(max_length=255)
    basic_httpsauth_user = models.CharField(max_length=255)
    basic_httpsauth_pass = models.CharField(max_length=255)

    def import_contacts(self, account):
        raise NotImplementedError("TODO: Implement RadicaleAccount.import_contacts(account)")

    def __str__(self):
        return f'radicale://{self.host}'

    @property
    def account_type(self):
        return 'Radicale'