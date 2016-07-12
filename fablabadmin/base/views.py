# -*- coding: utf-8 -*-
import autocomplete_light
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.forms import forms, CharField, Form, ModelForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from fablabadmin.base.models import Invoice, Resource, ResourceUsage, Contact, ContactStatus
from fablabadmin.base.utils import make_pdf
from material import LayoutMixin, Layout, Row, Fieldset, Field, Span6, Span8, Span4
from django.views.generic.edit import CreateView
from django.utils.translation import ugettext_lazy as _
from fablabadmin.settings import CONTACT_REGISTRATION_STATUS_ID
from django.views.decorators.csrf import csrf_exempt
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from django.db.models import Q
from django.shortcuts import get_object_or_404


def render_to_pdf(template_src, context_dict):
    try:
        result = make_pdf(template_src, context_dict)
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    except Exception as e:
        return HttpResponse('We had some errors<pre>%s</pre>' % e)


def index(request):
    resources = Resource.objects.all()
    return render(request, 'base/index.html', {'resources': resources})


class ContactRegisterForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'address', 'postal_code', 'city', 'phone', 'birth_year',
                  'email', 'status', 'education', 'profession', 'employer', 'interests']

    def __init__(self, *args, **kwargs):
        super(ContactRegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['address'].required = True
        self.fields['postal_code'].required = True
        self.fields['city'].required = True
        self.fields['phone'].required = True
        self.fields['birth_year'].required = True

    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    layout = Layout(Fieldset(_('Contact'),
                             Row('first_name', 'last_name'),
                             'email',
                             'address',
                             Row('postal_code', 'city'),
                             Row(Span8('phone'), Span4('birth_year')),
                    Fieldset(_('Informations'),
                             'education', 'profession', 'employer', 'interests'), 'captcha'))


def register(request):
    form = ContactRegisterForm()
    if request.method == 'POST':
        request.POST._mutable = True
        request.POST['status'] = CONTACT_REGISTRATION_STATUS_ID
        form = ContactRegisterForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=True)
            to = Contact.objects.filter(status__name='fablab_invoice').first()
            #TODO relative url configurable settings
            if to is not None:
                send_mail('[FabLab] Inscription',
                                       'Nouvelle inscription https://admin.fablab-lacote.ch/admin/base/contact/%d/change/' % (contact.id,),
                                       contact.email, [to.email])
                return HttpResponseRedirect(reverse('register_success'))
            else:
                #TODO handle error
                return HttpResponseRedirect(reverse('register_success'))


    return render(request, 'base/register_form.html', locals())


class ResourceUsageModelForm(autocomplete_light.ModelForm):
    class Meta:
        autocomplete_names = {'user': 'Contact', 'event': 'EventAutocomplete'}
        model = ResourceUsage
        fields = ('user', 'description', 'quantity', 'event', 'date')

    layout = Layout(Fieldset('Usage',
                             'user',
                             'description',
                             Row('quantity',
                             'date'),
                             'event'))


def resource(request, id=None, slug=None):
    resource = get_object_or_404(Resource, Q(id=id) | Q(slug=slug))
    last_usages = ResourceUsage.objects.filter(resource=resource).order_by('-date', '-id')[:5]
    if request.method == 'POST':
        form = ResourceUsageModelForm(request.POST)
        if form.is_valid():
            resource_usage = form.save(commit=False)
            resource_usage.resource = resource
            resource_usage.unit_price = resource.price
            resource_usage.save()
            if slug:
                return HttpResponseRedirect(reverse('resource', kwargs={'slug': slug}))
            if id:
                return HttpResponseRedirect(reverse('resource', kwargs={'id': id}))
    else:
        if request.user.is_authenticated() and request.user.contact:
            form = ResourceUsageModelForm(initial={"user": request.user.contact})
        else:
            form = ResourceUsageModelForm()
    return render(request, 'base/resource_usage.html', locals())


def change_lang(request):
    return render(request, 'base/change_lang.html')


def register_success(request):
    return HttpResponse(u"Votre inscription a bien été enregistrée. Une confirmation vous sera envoyée par e-mail au plus vite.")


@permission_required('base.change_invoice')
def invoice(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render_to_pdf(
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )

@permission_required('base.change_invoice')
def invoice_html(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render(request,
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )


@permission_required('base.change_invoice')
def mail_template(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    return render(request, 'base/mail/invoice.html',{
                'invoice': invoice
            })

@csrf_exempt
def dokuwiki_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            # the password verified for the user
            if user.is_active:
                grps = [x for x in user.groups.values_list('name', flat=True)]
                if user.contact:
                    grps += [user.contact.status.name]
                return JsonResponse({
                    "user": user.username,
                    "name": "%s %s" % (user.first_name, user.last_name),
                    "mail": user.email,
                    "grps": grps
                })
    return HttpResponse(status=403)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            # the password verified for the user
            # TODO use a real api and serializer?
            if user.is_active:
                return JsonResponse({
                    "user": {
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email
                    },
                })
    return HttpResponse(status=403)