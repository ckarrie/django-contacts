import base64
from urllib.request import urlopen

import vobject
from django.db import models
from django.utils.translation import gettext as _


class Phone(models.Model):
    phone_number = models.CharField(unique=True, max_length=70)

    def __str__(self):
        return self.phone_number


class UsageCategory(models.Model):
    text = models.CharField(max_length=255, help_text=_('i.e. Work, Private'))
    usage_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        if self.usage_index > 0:
            usage_nr = self.usage_index + 1
            return f'{self.text} #{usage_nr}'
        return f'{self.text}'


class Address(models.Model):
    street = models.CharField(max_length=255, blank=True, null=True)
    nr = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(_('city'), max_length=200, blank=True, null=True)
    province = models.CharField(_('province'), max_length=200, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True, null=True)
    country = models.CharField(_('country'), max_length=100)


class Email(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


class PersonGroup(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Website(models.Model):
    url = models.URLField()

    def __str__(self):
        return self.url


class InstantMessanger(models.Model):
    username = models.CharField(max_length=255)
    im_type = models.CharField(max_length=100, choices=(
        ('skype', 'Skype'),
        ('icq', 'ICQ'),
        ('aim', 'AIM'),
    ))

    def __str__(self):
        return f'{self.im_type}://{self.username}'


class Company(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(_('photo'), upload_to='contacts/companies/',
                             blank=True)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Person(models.Model):
    account = models.ForeignKey("Account", on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=100, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=200, null=True, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=200, blank=True, null=True)
    suffix = models.CharField(_('suffix'), max_length=50, blank=True, null=True)
    nickname = models.CharField(_('nickname'), max_length=100, blank=True, null=True)
    title = models.CharField(_('title'), max_length=200, blank=True)
    about = models.TextField(_('about'), blank=True)
    photo = models.ImageField(_('photo'), upload_to='contacts/person/',
                              blank=True)
    photo_url = models.URLField(null=True, blank=True)
    google_resource_name = models.CharField(max_length=255, null=True, blank=True, editable=False)
    birthday = models.DateField(null=True, blank=True)

    def photo_to_base64(self):
        if self.photo_url:
            return base64.b64encode(urlopen(self.photo_url).read())

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.last_name}, {self.first_name}'
        if self.first_name:
            return f'{self.first_name}'
        if self.last_name:
            return f'{self.last_name}'
        if self.nickname:
            return self.nickname
        return '?'

    @property
    def first_photo_url(self):
        if self.photo:
            return self.photo.url
        if self.photo_url:
            return self.photo_url
        return 'none.png'

    def as_vcf(self, absolute_uri=None):
        data = {
            'N': f'{self.last_name};{self.first_name}',  # N:<Nachname>;<Vorname>;<zusätzliche Vornamen>;<Präfix>;<Suffix>
            'FN': str(self),
            'uid': f'contact-{self.pk}',
            'VERSION': '4.0'

        }

        for phonecon in self.personphoneconnection_set.filter(phone__phone_number__isnull=False):
            data[f'TEL;VALUE=uri;TYPE={phonecon.usage.text}'] = f'tel:{phonecon.phone.phone_number}'

        for emailcon in self.personemailconnection_set.filter(email__email__isnull=False):
            data[f'EMAIL;TYPE={emailcon.usage.text}'] = emailcon.email.email

        if self.nickname:
            data['NICKNAME'] = self.nickname

        absolute_photo_url = None
        if self.photo:
            absolute_photo_url = absolute_uri + self.photo.url
        if self.photo_url:
            absolute_photo_url = self.photo_url

        #if absolute_photo_url:
        #    data['PHOTO'] = absolute_photo_url
        photo_base64 = self.photo_to_base64()
        if photo_base64:
            photo_base64 = photo_base64.decode('utf-8')
            data['PHOTO'] = f'data:image/jpeg;base64,{photo_base64}'

        vcard = vobject.readOne('\n'.join([f'{k}:{v}' for k, v in data.items()]))
        vcard.name = 'VCARD'
        vcard.useBegin = True
        return vcard

    def as_vcf_serialized(self, absolute_uri=None):
        return self.as_vcf(absolute_uri=absolute_uri).serialize()


