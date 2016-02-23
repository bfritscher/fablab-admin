from django import forms
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.shortcuts import render
from material import Layout, Row, Span5, Span2
from django.utils.translation import ugettext_lazy as _

from fablabadmin.base.models import Contact


class ContactProfileModelForm(ModelForm):
    class Meta:
        model = Contact
        widgets = {
            'payment_info': forms.Textarea(
                attrs={'placeholder': _('IBAN or other to receive refunds')}),
        }
        fields = ('email', 'phone', 'address', 'postal_code', 'city', 'country', 'payment_info')
    layout = Layout(
        Row('email', 'phone'),
        'address',
        Row(Span2('postal_code'), Span5('city'),Span5('country') ),
        'payment_info')


class ContactProfileDetailModelForm(ModelForm):
    class Meta:
        model = Contact
        fields = ('birth_year', 'education', 'profession', 'employer', 'interests')
    layout = Layout('birth_year', 'education', 'profession', 'employer', 'interests')


@login_required
def profile(request):
    profile_form = ContactProfileModelForm(instance=request.user.contact)
    profile_detail_form = ContactProfileDetailModelForm(instance=request.user.contact)

    return render(request, 'accounts/profile.html', locals())


@login_required
def profile_edit(request):
    profile_form = ContactProfileModelForm(instance=request.user.contact)
    profile_detail_form = ContactProfileDetailModelForm(instance=request.user.contact)

    if request.method == 'POST':
        profile_form = ContactProfileModelForm(request.POST, instance=request.user.contact)
        if profile_form.is_valid():
            profile_form.save(commit=True)
        profile_detail_form = ContactProfileDetailModelForm(request.POST, instance=request.user.contact)
        if profile_detail_form.is_valid():
            profile_detail_form.save(commit=True)

    return render(request, 'accounts/profile_edit.html', locals())