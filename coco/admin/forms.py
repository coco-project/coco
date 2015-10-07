from coco.core.models import BackendUser, CollaborationGroup, Share
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class CollaborationGroupAdminForm(forms.ModelForm):

    """
    :link https://djangosnippets.org/snippets/2452/
    """

    admins = forms.ModelMultipleChoiceField(
        queryset=BackendUser.objects.all(),
        widget=FilteredSelectMultiple('Admins', False),
        required=False
    )
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
            initial['admins'] = instance.admins.all()
            initial['users'] = instance.get_users()
            kwargs['initial'] = initial
        super(CollaborationGroupAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        :inherit.
        """
        group = super(CollaborationGroupAdminForm, self).save(commit=commit)
        if commit:
            # admins
            for admin in group.admins.all():
                if admin not in self.cleaned_data['admins']:
                    group.remove_admin(admin)
            for admin in self.cleaned_data['admins']:
                group.add_admin(admin)
            # users
            for user in group.get_users():
                if user not in self.cleaned_data['users']:
                    group.remove_user(user)
            for user in self.cleaned_data['users']:
                group.add_user(user)
        else:
            old_save_m2m = self.save_m2m

            def new_save_m2m():
                old_save_m2m()
                # admins
                for admin in group.admins.all():
                    if admin not in self.cleaned_data['admins']:
                        group.remove_admin(admin)
                for admin in self.cleaned_data['admins']:
                    group.add_admin(admin)
                # users
                for user in group.get_users():
                    if user not in self.cleaned_data['users']:
                        group.remove_user(user)
                for user in self.cleaned_data['users']:
                    group.add_user(user)
            self.save_m2m = new_save_m2m
        return group

    class Meta:
        model = CollaborationGroup
        exclude = []


class ShareAdminForm(forms.ModelForm):

    """
    :link https://djangosnippets.org/snippets/2452/
    """

    def __init__(self, *args, **kwargs):
        """
        :inherit.
        """
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['access_groups'] = instance.access_groups.all()
            kwargs['initial'] = initial
        super(ShareAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        :inherit.
        """
        share = super(ShareAdminForm, self).save(commit=commit)
        if commit:
            for access_group in share.access_groups.all():
                if access_group not in self.cleaned_data['access_groups']:
                    share.remove_access_group(access_group)
            for access_group in self.cleaned_data['access_groups']:
                share.add_access_group(access_group)
        else:
            old_save_m2m = self.save_m2m

            def new_save_m2m():
                old_save_m2m()
                for access_group in share.access_groups.all():
                    if access_group not in self.cleaned_data['access_groups']:
                        share.remove_access_group(access_group)
                for access_group in self.cleaned_data['access_groups']:
                    share.add_access_group(access_group)
            self.save_m2m = new_save_m2m
        return share

    class Meta:
        model = Share
        exclude = []
