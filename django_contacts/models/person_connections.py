from django.db import models


class PersonPhoneConnection(models.Model):
    phone = models.ForeignKey("Phone", on_delete=models.SET_NULL, null=True, blank=True)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonAddressConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    address = models.ForeignKey("Address", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonEmailConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    email = models.ForeignKey("Email", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonGroupConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    group = models.ForeignKey("PersonGroup", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonWebsiteConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    website = models.ForeignKey("Website", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonCompanyConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)


class PersonIMConnection(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    im = models.ForeignKey("InstantMessanger", on_delete=models.CASCADE)
    usage = models.ForeignKey("UsageCategory", on_delete=models.SET_NULL, null=True, blank=True)