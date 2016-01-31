import autocomplete_light
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from fablabadmin.base.models import Invoice, Resource, ResourceUsage
from fablabadmin.base.utils import make_pdf


def render_to_pdf(template_src, context_dict):
    try:
        result = make_pdf(template_src, context_dict)
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    except Exception as e:
        return HttpResponse('We had some errors<pre>%s</pre>' % e)


def index(request):
    resources = Resource.objects.all()
    return render(request, 'base/index.html', {'resources': resources})


class ResourceUsageModelForm(autocomplete_light.ModelForm):
    class Meta:
        autocomplete_names = {'user': 'Contact', 'event': 'EventAutocomplete'}
        model = ResourceUsage
        fields = ('user', 'description', 'quantity', 'unit_price', 'event')


def resource(request, id):
    resource = Resource.objects.get(id=id)
    last_usages = ResourceUsage.objects.filter(resource=resource).order_by('-date', '-id')[:5]
    form = ResourceUsageModelForm()
    if request.method == 'POST':
        form = ResourceUsageModelForm(request.POST)
        if form.is_valid():
            resource_usage = form.save(commit=False)
            resource_usage.resource = resource
            resource_usage.save()
            return HttpResponseRedirect(reverse('resource', kwargs={'id': id}))
    return render(request, 'base/resource_usage.html', locals())


def change_lang(request):
    return render(request, 'base/change_lang.html')

@permission_required('invoice.can_view')
def invoice(request, id):
    print 'test:', id
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render_to_pdf(
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )


@permission_required('invoice.can_view')
def invoice_html(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    #Retrieve data or whatever you need
    return render(request,
            'base/invoice.html',
            {
                'invoice': invoice
            }
        )


@permission_required('invoice.can_view')
def mail_template(request, id):
    invoice = Invoice.objects.prefetch_related('entries').get(id=id)
    return render(request, 'base/mail/invoice.html',{
                'invoice': invoice
            })