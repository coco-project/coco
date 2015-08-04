from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from ipynbsrv.core.models import BackendUser, CollaborationGroup


class CollaborationGroupAdminForm(forms.ModelForm):

    """
    :link https://djangosnippets.org/snippets/2452/
    """

    users = forms.ModelMultipleChoiceField(
        queryset=BackendUser.objects.all(),
        widget=FilteredSelectMultiple('Users', False),
        required=False
    )


    def __init__(self, *args, **kwargs):
        """
        :inherit.
        """
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['users'] = instance.get_members()
            kwargs['initial'] = initial
        super(CollaborationGroupAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        :inherit.
        """
        group = super(CollaborationGroupAdminForm, self).save(commit=commit)
        if commit:
            group.user_set.clear()
            for user in self.cleaned_data['users']:
                group.add_member(user)
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                group.user_set.clear()
                for user in self.cleaned_data['users']:
                    group.add_member(user)
            self.save_m2m = new_save_m2m
        return group

    class Meta:
        model = CollaborationGroup
        exclude = []
