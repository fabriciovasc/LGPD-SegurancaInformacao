# coding: utf-8
from django import template
from django.forms import widgets
from django.forms.fields import DateField
from django.template.loader import get_template
from django.utils.safestring import SafeText

register = template.Library()


def add_css_class_widget(widget, css_class):
    if 'class' in widget.attrs:
        _css_class = '%s %s' % (widget.attrs['class'], css_class)
    else:
        _css_class = css_class
    widget.attrs['class'] = _css_class


def get_widget(field):
    try:
        widget = field.field.widget
    except Exception:
        if isinstance(field, str) or isinstance(field, SafeText):
            return field
        raise ValueError("Expected a Field, got a %s" % type(field))
    return widget


@register.filter
def as_bs4(field, opt=None):
    if not field:
        return ''

    widget = get_widget(field)
    options = opt.split(",") if opt else ['']
    inline = True if "inline" in options else False
    vertical = True if "vertical" in options else False

    if field.errors:
        add_css_class_widget(widget, 'is-invalid')

    if isinstance(field.field, DateField):
        input_type = u'date'
        add_css_class_widget(widget, 'datepicker')

    if isinstance(widget, widgets.TextInput):
        input_type = u'text'
        add_css_class_widget(widget, 'form-control')

    elif isinstance(widget, widgets.Textarea):
        input_type = u'textarea'
        add_css_class_widget(widget, 'form-control')

    elif isinstance(widget, widgets.CheckboxInput):
        input_type = u'checkbox'
        add_css_class_widget(widget, 'form-check-input')

    elif isinstance(widget, widgets.CheckboxSelectMultiple):
        input_type = u'multicheckbox'
        add_css_class_widget(widget, 'form-check-input')

    elif isinstance(widget, widgets.RadioSelect):
        input_type = u'radioset'
        add_css_class_widget(widget, 'form-check-input')

    elif isinstance(widget, widgets.Select):
        input_type = u'select'
        add_css_class_widget(widget, 'form-control')

    elif isinstance(widget, widgets.ClearableFileInput):
        input_type = u'select'
        add_css_class_widget(widget, 'form-control')

    else:
        input_type = u'default'
        add_css_class_widget(widget, 'form-control')

    return get_template("bootstrap4_form/field.html").render({
        'field': field,
        'col': options[0],
        'widget': widget,
        'inline': inline,
        'vertical': vertical,
        'input_type': input_type,
    })


@register.filter
def as_bs4_custom(field, opt=None):
    if not field:
        return ''

    widget = get_widget(field)
    options = opt.split(",") if opt else ['']
    inline = True if "inline" in options else False
    vertical = True if "vertical" in options else False

    if field.errors:
        add_css_class_widget(widget, 'is-invalid')

    if isinstance(widget, widgets.CheckboxInput):
        input_type = u'checkbox'
        add_css_class_widget(widget, 'custom-control-input')

    elif isinstance(widget, widgets.CheckboxSelectMultiple):
        input_type = u'multicheckbox'
        add_css_class_widget(widget, 'custom-control-input')

    elif isinstance(widget, widgets.RadioSelect):
        input_type = u'radioset'
        add_css_class_widget(widget, 'custom-control-input')

    else:
        input_type = u'default'
        add_css_class_widget(widget, 'form-control')

    return get_template("bootstrap4_form/field.html").render({
        'field': field,
        'col': options[0],
        'widget': widget,
        'inline': inline,
        'vertical': vertical,
        'input_type': input_type,
        'custom': True
    })


@register.filter()
def search_form(form, buttons=None):
    '''
    <input type="text" name="q" id="id_q" class="form-control" aria-label="..." value="">
    '''

    # loads the bootstratwitter 3 template
    html = template.loader.get_template('bootstrap4_form/search_field.html')
    return html.render({'form': form})
