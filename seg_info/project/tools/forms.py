from functools import reduce

from django import forms
from django.conf import settings

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.text import smart_split
from django.utils.translation import ugettext_lazy as _

DEFAULT_STOPWORDS = ('de,o,a,os,as')


DATABASE_ENGINE = settings.DATABASES['default']['ENGINE']


class BaseSearchForm(forms.Form):
    """See http://gregbrown.co.nz/code/django-simple-search/ for details"""

    STOPWORD_LIST = DEFAULT_STOPWORDS.split(',')
    DEFAULT_OPERATOR = Q.__and__
    # DEFAULT_OPERATOR = staticmethod(Q.__and__)
    # DEFAULT_OPERATOR = (lambda self, *args, **kwargs: Q.__and__(*args, **kwargs))

    q = forms.CharField(label=_('Search'), required=False)

    def clean_q(self):
        return self.cleaned_data['q'].strip()

    order_by = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        abstract = True

        base_qs = None

        # example: ['name', 'category__name', '@description', '=id']
        search_fields = None

        # should be a list of  pairs, of the form ('field1,field2', WEIGHTING)
        # where WEIGHTING is an integer. Assumes the relevant indexes have been
        # created

        fulltext_indexes = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs = {'placeholder': self.get_q_placeholder()}

    def get_advanced_search_fields(self):
        return [field for idx, field in enumerate(self) if idx not in (0, 1)]

    def get_q_placeholder(self):
        return ''

    def construct_search(self, field_name, first):
        if field_name.startswith('^'):
            if first:
                return "%s__istartswith" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            if DATABASE_ENGINE == 'django.db.backends.mysql':
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def get_text_query_bits(self, query_string):
        """filter stopwords but only if there are useful words"""

        split_q = list(smart_split(query_string))
        filtered_q = []

        for bit in split_q:
            if bit not in self.STOPWORD_LIST:
                filtered_q.append(bit)

        if len(filtered_q):
            return filtered_q
        else:
            return split_q

    def get_default_operator(self):
        return type(self).DEFAULT_OPERATOR

    def get_text_search_query(self, query_string):
        filters = []
        first = True

        for bit in self.get_text_query_bits(query_string):
            or_queries = [Q(**{self.construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
            filters.append(reduce(Q.__or__, or_queries))
            first = False

        if len(filters):
            return reduce(
                self.get_default_operator(),
                filters
            )
        else:
            return False

    def construct_filter_args(self, cleaned_data):
        args = []

        # if its an instance of Q, append to filter args
        # otherwise assume an exact match lookup
        for field in cleaned_data:

            if hasattr(self, 'prepare_%s' % field):
                q_obj = getattr(self, 'prepare_%s' % field)()
                if q_obj:
                    args.append(q_obj)
            elif isinstance(cleaned_data[field], Q):
                args.append(cleaned_data[field])
            elif field == 'order_by':
                pass  # special case - ordering handled in get_result_queryset
            elif cleaned_data[field]:
                if isinstance(cleaned_data[field], list) or isinstance(cleaned_data[field], QuerySet):
                    args.append(Q(**{field + '__in': cleaned_data[field]}))
                else:
                    args.append(Q(**{field: cleaned_data[field]}))

        return args

    def get_result_queryset(self):
        qs = self.Meta.base_qs

        cleaned_data = self.cleaned_data.copy()
        query_text = cleaned_data.pop('q', None)

        qs = qs.filter(*self.construct_filter_args(cleaned_data))

        if query_text:
            fulltext_indexes = getattr(self.Meta, 'fulltext_indexes', None)
            if DATABASE_ENGINE == 'django.db.backends.mysql' and fulltext_indexes:
                # cross-column fulltext search if db is mysql, otherwise use default behaviour.
                # We're assuming the appropriate fulltext index has been created
                match_bits = []
                params = []
                for index in fulltext_indexes:
                    match_bits.append('MATCH(%s) AGAINST (%%s) * %s' % index)
                    params.append(query_text)

                match_expr = ' + '.join(match_bits)

                qs = qs.extra(
                    select={'relevance': match_expr},
                    where=(match_expr,),
                    params=params,
                    select_params=params,
                    order_by=('-relevance',)
                )

            else:
                # construct text search for sqlite, or for when no fulltext indexes are defined
                text_q = self.get_text_search_query(query_text)
                if text_q:
                    qs = qs.filter(text_q)
                else:
                    qs = qs.none()

        if cleaned_data.get('order_by', None):
            qs = qs.order_by(*cleaned_data['order_by'].split(','))

        return qs


class RelatedObjInitMixin(object):
    related_obj_name_list = []

    def __init__(self, *args, **kwargs):
        for related_obj_name in self.related_obj_name_list:
            setattr(self, related_obj_name, kwargs.pop(related_obj_name))
        super().__init__(*args, **kwargs)


class RelatedObjSaveMixin(object):
    related_obj_name_list = []

    def save(self, commit=True):
        for related_obj_name in self.related_obj_name_list:
            setattr(self.instance, related_obj_name, getattr(self, related_obj_name))
        return super().save(commit=commit)


class RelatedObjModelMixin(RelatedObjInitMixin, RelatedObjSaveMixin):
    pass


class CustomInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        super().__init__(*args, **kwargs)

    def _construct_form(self, *args, **kwargs):
        kwargs['request_user'] = self.request_user
        return super()._construct_form(*args, **kwargs)


class UserAddUpdFormMixin(forms.ModelForm):
    '''recebe um usuário e usa este para "salvar" como  `user_add` ou `user_upd`.

     form para ser usado com os modelos  'UserDateAdd'e 'UserDateUpd'.
    a vew  deve ser passado um KEYWORD Parameter com o nome de `request_user`

    :nota:
        Existe um view mixin que passa o param  = `core.views.UserDateAddUpdFormMixin`.

    kwargs:
        request_user (type:User):  geralmente é passado o  request.user

    :notes:
        O `request_user` fica disponível após o __init__ do Base ser executado.
        O  atributo `request_user` da classe contém o request user (`self.request_user`).

        :Exemplo:

            class TicketForm(UserAddUpdFormMixin):

                def __init__(self, *args, **kwargs):
                    super(TicketForm, self).__init__(*args, **kwargs)
                    # usa o self.request_user para filtrar choices de um field
                    self.fields['project'].quersyet = Project.objects.by_user(self.request_user)
    '''

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.user_upd = self.request_user
        if not hasattr(self.instance, 'user_add'):
            self.instance.user_add = self.request_user
        return super().save(commit=commit)
