import vobject
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string

from lxml import etree

from . import models


LIMIT_CONTACTS = None


class CardDAVView(generic.View):
    http_method_names = ['propfind', 'report']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CardDAVView, self).dispatch(request, *args, **kwargs)

    def get_xml(self):
        return b""""""

    def propfind(self, request, *args, **kwargs):
        print("CardDAVView.propfind request\n", request.body.decode())

        root = etree.fromstring(request.body)

        has_resourcetype = root.xpath('.//*[local-name()="prop"]/*[local-name()="resourcetype"]')
        has_displayname = root.xpath('.//*[local-name()="prop"]/*[local-name()="displayname"]')
        has_user_principal = root.xpath('.//*[local-name()="prop"]/*[local-name()="current-user-principal"]')
        has_user_privilege = root.xpath('.//*[local-name()="prop"]/*[local-name()="current-user-privilege-set"]')
        has_getctag = root.xpath('.//*[local-name()="prop"]/*[local-name()="getctag"]')

        contacts = []
        addressbook = models.AddressBook.objects.get(pk=kwargs['pk'])
        if has_getctag:
            contacts = addressbook.get_persons()
            if LIMIT_CONTACTS:
                contacts = contacts[:LIMIT_CONTACTS]

        xml = render_to_string('django_contacts/xml/multistatus.xml', context={
            'has_resourcetype': bool(has_resourcetype),
            'has_displayname': bool(has_displayname),
            'has_user_principal': bool(has_user_principal),
            'has_user_privilege': bool(has_user_privilege),
            'has_getctag': bool(has_getctag),
            'url_path': request.build_absolute_uri(request.path),
            'addressbook': addressbook,
            'contacts': contacts
        })

        print(xml)

        #xml = self.get_xml()
        resp = HttpResponse(content=xml, content_type='application/xml; charset=utf-8', status=207)
        return resp

    def report(self, request, *args, **kwargs):
        print("CardDAVView.report request\n", request.body.decode())
        root = etree.fromstring(request.body)
        print("root.tag", root.tag)
        is_addressbook_multiget = 'addressbook-multiget' in root.tag
        need_getetag = bool(root.xpath('.//*[local-name()="prop"]/*[local-name()="getetag"]'))
        need_adress_data = bool(root.xpath('.//*[local-name()="prop"]/*[local-name()="address-data"]'))
        hrefs = root.xpath('.//*[local-name()="href"]')

        print("is_addressbook_multiget", is_addressbook_multiget)
        print("need_getetag", need_getetag)
        print("need_adress_data", need_adress_data)
        print("hrefs", [elem.text for elem in hrefs])

        addressbook = models.AddressBook.objects.get(pk=kwargs['pk'])

        contacts = []
        if need_getetag:
            contacts = addressbook.get_persons()
            if LIMIT_CONTACTS:
                contacts = contacts[:LIMIT_CONTACTS]

        for contact in contacts:
            contact.as_vcf_rendered = contact.as_vcf_serialized(absolute_uri=request.build_absolute_uri())

        xml = render_to_string('django_contacts/xml/list_contacts.xml', context={
            'url_path': request.build_absolute_uri(request.path),
            'addressbook': addressbook,
            'contacts': contacts
        })
        print("========================= RESPONSE =========================")

        print(xml)
        resp = HttpResponse(content=xml, content_type='application/xml; charset=utf-8', status=207)
        return resp


class CardDAVContactView(generic.View):
    http_method_names = ['put']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CardDAVContactView, self).dispatch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        print(kwargs)
        print("CardDAVContactView.put request\n", request.body.decode())
        # content ist eine vcard
        vcard = vobject.readOne(request.body.decode())
        print(vcard)
        resp = HttpResponse(content=b"", content_type='application/v-card; charset=utf-8', status=200)
        return resp


class WellKnownView(generic.RedirectView):
    type = 'caldav'

    def get_redirect_url(self):
        #return self.request.build_absolute_uri("")
        url = self.request.build_absolute_uri("/dav/")
        print("WK rd url", url)
        return url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

