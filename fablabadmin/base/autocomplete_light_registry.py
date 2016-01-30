import autocomplete_light.shortcuts as al

# This will generate a PersonAutocomplete class.
from fablabadmin.base.models import Contact


class ContactAutocomplete(al.AutocompleteModelBase):
    search_fields=['^first_name', 'last_name']
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'Other model name ?',
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery.
        'data-autocomplete-minimum-characters': 1,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 4,
        # Enable modern-style widget !
        'class': 'modern-style',
    }

al.register(ContactAutocomplete, name='Contact',
            choices=Contact.objects.all())
al.register(ContactAutocomplete, name='Member',
            choices=Contact.objects.filter(status__is_member=True))