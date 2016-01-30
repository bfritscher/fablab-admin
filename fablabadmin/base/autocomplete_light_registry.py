import autocomplete_light.shortcuts as al
from django.utils.translation import ugettext_lazy as _

# This will generate a PersonAutocomplete class.
from fablabadmin.base.models import Contact, Event, Resource


class ContactAutocomplete(al.AutocompleteModelBase):
    search_fields=['^first_name', 'last_name']
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': _('contact name'),
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery.
        'data-autocomplete-minimum-characters': 0,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 5,
        # Enable modern-style widget !
        'class': 'modern-style',
    }


class EventAutocomplete(al.AutocompleteModelBase):
    search_fields=['^title']
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': _('event title'),
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery.
        'data-autocomplete-minimum-characters': 0,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 5,
        # Enable modern-style widget !
        'class': 'modern-style',
    }


class ResourceAutocomplete(al.AutocompleteModelBase):
    search_fields=['^name']
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': _('resource name'),
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery.
        'data-autocomplete-minimum-characters': 0,
    }
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 5,
        # Enable modern-style widget !
        'class': 'modern-style',
    }


al.register(Resource, ResourceAutocomplete)
al.register(Event, EventAutocomplete)
al.register(ContactAutocomplete, name='Contact',
            choices=Contact.objects.all())
al.register(ContactAutocomplete, name='Member',
            choices=Contact.objects.filter(status__is_member=True))