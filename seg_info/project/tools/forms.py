from django import forms

class UserAddUpdFormMixin(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.user_upd = self.request_user
        if not hasattr(self.instance, 'user_add'):
            self.instance.user_add = self.request_user
        return super().save(commit=commit)
