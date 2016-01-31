from django import template

register = template.Library()


@register.filter(name='add_css')
def add_css(field, css):
    return field.as_widget(attrs={"class": css})


#http://stackoverflow.com/questions/414679/add-class-to-django-label-tag-output
@register.filter(is_safe=True)
def label_with_classes(value, arg):
    return value.label_tag(attrs={'class': arg})
