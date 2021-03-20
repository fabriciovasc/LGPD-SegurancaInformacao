# coding: utf-8
import re

from django.apps import apps
from django import template
try:
    from django.urls import reverse  # noqa
except ImportError:
    from django.core.urlresolvers import reverse

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.base import Node
from django.template.loader import get_template
from django.utils.safestring import mark_safe

kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

register = template.Library()

get_model = apps.get_model


class DeleteNode(Node):
    def __init__(
        self,
        app_model,
        object_id,
        message,
        next_url,
        btn_class=None,
        btn_text=None,
        cannot_delete_message=None
    ):
        self.app_model = template.Variable(app_model)
        self.object_id = template.Variable(object_id)
        self.message = template.Variable(message)
        self.next_url = template.Variable(next_url)

        if btn_class:
            self.btn_class = template.Variable(btn_class)
        else:
            self.btn_class = None

        if btn_text:
            self.btn_text = template.Variable(btn_text)
        else:
            self.btn_text = ""

        if cannot_delete_message:
            self.cannot_delete_message = template.Variable(cannot_delete_message)
        else:
            self.cannot_delete_message = ""

    def render(self, context):
        object_id = self.object_id.resolve(context)
        app_model = self.app_model.resolve(context)
        message = self.message.resolve(context)
        next_url = self.next_url.resolve(context)

        if self.btn_class:
            btn_class = self.btn_class.resolve(context)
        else:
            btn_class = "btn btn-outline-danger"

        if self.btn_text:
            btn_text = self.btn_text.resolve(context)
        else:
            btn_text = ""

        if self.cannot_delete_message:
            try:
                cannot_delete_message = self.cannot_delete_message.resolve(context)
            except Exception:
                cannot_delete_message = settings.DISABLED_DELETE_MESSAGE
        else:
            cannot_delete_message = settings.DISABLED_DELETE_MESSAGE

        can_delete = True
        app_name, model_name = app_model.split('.', 1)
        obj = get_object_or_404(get_model(app_name, model_name), pk=object_id)
        template = get_template('nectools/components/delete_button.html')

        if hasattr(obj, 'user_can_delete'):
            can_delete = getattr(obj, 'user_can_delete')
            can_delete = can_delete(context['request'].user)

        elif hasattr(obj, 'can_delete'):
            can_delete = getattr(obj, 'can_delete')
            if callable(can_delete):
                can_delete = can_delete()

        return mark_safe(template.render({
            'can_delete': can_delete,
            'message': message,
            'next_url': next_url,
            'url': reverse('generic_delete', args=(app_model, object_id)),
            'btn_class': btn_class,
            'btn_text': btn_text,
            'cannot_delete_message': cannot_delete_message
        }))


@register.tag
def user_can_delete(parser, token):
    num_of_req_params = 4
    bits = token.split_contents()

    if len(bits) < num_of_req_params:
        raise template.TemplateSyntaxError(
            "'%s' takes at least three arguments"
            " (app, model, object_id)" % bits[0]
        )

    app_model = bits[1]
    object_id = bits[2]
    message = bits[3]
    next_url = bits[4]

    if len(bits) > num_of_req_params + 1:
        btn_class = bits[5]
    else:
        btn_class = None

    if len(bits) > num_of_req_params + 2:
        btn_text = bits[6]
    else:
        btn_text = None

    if len(bits) > num_of_req_params + 3:
        cannot_delete_message = bits[7]
    else:
        cannot_delete_message = None

    return DeleteNode(
        app_model, object_id, message,
        next_url, btn_class, btn_text,
        cannot_delete_message
    )
