from django_admin_conf_vars.models import ConfigurationVariable
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from ipynbsrv.admin.forms import CollaborationGroupAdminForm
from ipynbsrv.core.models import *


class CoreAdminSite(admin.AdminSite):

    """
    ipynbsrv application admin site.
    """

    site_header = 'ipynbsrv Administration'
    site_title = 'ipynbsrv - Administration'

    index_title = 'Management'


class BackendAdmin(admin.ModelAdmin):

    """
    Admin model for the `Backend` model.
    """

    list_display = ['module', 'klass', 'arguments']
    list_filter = [
        'kind'
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['kind', 'module', 'klass', 'arguments']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['kind']
        else:
            return []


class CollaborationGroupAdmin(GroupAdmin):

    """
    Admin model for the `CollaborationGroup` model.
    """

    list_display = ['name']
    list_filter = ['creator', 'is_public']

    form = CollaborationGroupAdminForm
    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'creator', 'admins']
        }),
        ('Membership Options', {
            'fields': ['users']
        }),
        ('Visibility Options', {
            'fields': ['is_public']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['creator', 'name']
        else:
            return []


class ConfigurationVariableAdmin(admin.ModelAdmin):

    """
    Admin model for the `ConfigurationVariable` model.
    """

    list_display = ['name']

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'description', 'value']
        })
    ]

    readonly_fields = ['description', 'name']

    def has_add_permission(self, request):
        """
        :inherit.
        """
        return False


class ContainerAdmin(admin.ModelAdmin):

    """
    Admin model for the `Container` model.
    """

    actions = [
        'restart_containers',
        'resume_containers',
        'start_containers',
        'stop_containers',
        'suspend_containers'
    ]

    list_display = ['name', 'description', 'owner', 'is_clone', 'is_running', 'is_suspended']
    list_filter = [
        ('clone_of', admin.RelatedOnlyFieldListFilter),
        ('image', admin.RelatedOnlyFieldListFilter),
        ('owner', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'description', 'owner']
        }),
        ('Creation Properties', {
            'fields': ['image', 'clone_of', 'server']
        }),
        ('Backend Properties', {
            'classes': ['collapse'],
            'fields': ['backend_pk']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['backend_pk', 'clone_of', 'image', 'name', 'owner', 'server']
        else:
            return ['backend_pk']

    def response_change(self, request, obj):
        """
        :inherit.
        """
        stay = False
        if '_clone' in request.POST or '_commit' in request.POST or '_snapshot' in request.POST:
            name = request.POST.get('_container-action-name')
            if len(name) != 0:
                try:
                    if '_clone' in request.POST:
                        ret = obj.clone(name)
                        url = reverse('admin:core_container_change', args=(ret.id,))
                    elif '_commit' in request.POST:
                        ret = obj.commit(name)
                        url = reverse('admin:core_containerimage_change', args=(ret.id,))
                    else:
                        ret = obj.create_snapshot(name)
                        url = reverse('admin:core_containersnapshot_change', args=(ret.id,))
                    self.message_user(request, "Container action completed successfully.")
                    return HttpResponseRedirect(url)
                except Exception:
                    self.message_user(request, "Operation failed.", messages.ERROR)
            else:
                self.message_user(request, "The name field is required.", messages.WARNING)
            stay = True
        elif '_restart' in request.POST:
            self.restart_containers(request, [obj])
            stay = True
        elif '_resume' in request.POST:
            self.resume_containers(request, [obj])
            stay = True
        elif '_start' in request.POST:
            self.start_containers(request, [obj])
            stay = True
        elif '_stop' in request.POST:
            self.stop_containers(request, [obj])
            stay = True
        elif '_suspend' in request.POST:
            self.suspend_containers(request, [obj])
            stay = True

        if stay:
            return HttpResponseRedirect(reverse('admin:core_container_change', args=(obj.id,)))
        return super(ContainerAdmin, self).response_change(request, obj)

    def restart_containers(self, request, queryset):
        """
        Restart all selected containers.
        """
        failed = 0
        restarted = 0
        for container in queryset:
            try:
                container.restart()
                restarted += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully restarted %i container(s). %i failed." % (restarted, failed)
        )
    restart_containers.short_description = "Restart selected containers"

    def resume_containers(self, request, queryset):
        """
        Suspend all selected containers.
        """
        failed = 0
        resumed = 0
        for container in queryset:
            try:
                container.resume()
                resumed += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully resumed %i container(s). %i failed." % (resumed, failed)
        )
    resume_containers.short_description = "Resume selected containers"

    def start_containers(self, request, queryset):
        """
        Start all selected containers.
        """
        failed = 0
        started = 0
        for container in queryset:
            try:
                container.start()
                started += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully started %i container(s). %i failed." % (started, failed)
        )
    start_containers.short_description = "Start selected containers"

    def stop_containers(self, request, queryset):
        """
        Start all selected containers.
        """
        failed = 0
        stopped = 0
        for container in queryset:
            try:
                container.stop()
                stopped += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully stopped %i container(s). %i failed." % (stopped, failed)
        )
    stop_containers.short_description = "Stop selected containers"

    def suspend_containers(self, request, queryset):
        """
        Suspend all selected containers.
        """
        failed = 0
        suspended = 0
        for container in queryset:
            try:
                container.suspend()
                suspended += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully suspended %i container(s). %i failed." % (suspended, failed)
        )
    suspend_containers.short_description = "Suspend selected containers"


class ContainerImageAdmin(admin.ModelAdmin):

    """
    Admin model for the `ContainerImage` model.
    """

    list_display = ['get_friendly_name', 'description', 'is_internal', 'is_public']
    list_filter = [
        'is_internal',
        'is_public',
        ('owner', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'description', 'owner']
        }),
        ('Backend Properties', {
            'classes': ['collapse'],
            'fields': ['backend_pk', 'command', 'protected_port', 'public_ports']
        }),
        ('Visibility Options', {
            'fields': ['is_public']
        })
    ]

    def get_friendly_name(self, obj):
        """
        Get the container image's friendly name.
        """
        return obj.get_friendly_name()
    get_friendly_name.short_description = 'Friendly name'

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['backend_pk', 'command', 'name', 'protected_port', 'public_ports', 'owner']
        else:
            return []


class ContainerSnapshotAdmin(admin.ModelAdmin):

    """
    Admin model for the `ContainerSnapshot` model.
    """

    actions = [
        'restore_snapshots'
    ]

    list_display = ['name', 'description', 'container']
    list_filter = [
        ('container', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'description']
        }),
        ('Creation Properties', {
            'fields': ['container']
        }),
        ('Backend Properties', {
            'classes': ['collapse'],
            'fields': ['backend_pk']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['backend_pk', 'container', 'name']
        else:
            return ['backend_pk']

    def response_change(self, request, obj):
        """
        :inherit.
        """
        if '_restore' in request.POST:
            self.restore_snapshots(request, [obj])
            request.POST['_continue'] = True

        return super(ContainerSnapshotAdmin, self).response_change(request, obj)

    def restore_snapshots(self, request, queryset):
        """
        Suspend all selected containers.
        """
        failed = 0
        restored = 0
        for snapshot in queryset:
            try:
                snapshot.restore()
                restored += 1
            except Exception:
                failed += 1
        self.message_user(
            request,
            "Successfully restored %i container snapshot(s). %i failed." % (restored, failed)
        )
    restore_snapshots.short_description = "Restore selected container snapshots"


class GroupAdmin(admin.ModelAdmin):

    """
    Admin model for the `Group` model.
    """

    fieldsets = [
        ('General Properties', {
            'fields': ['name']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['name']
        else:
            return []


class NotificationAdmin(admin.ModelAdmin):

    """
    Admin model for the `Notification` model.
    """

    list_display = ['message', 'date', 'sender', 'has_related_object']
    list_filter = [
        ('sender', admin.RelatedOnlyFieldListFilter),
        'notification_type',
        ('container', admin.RelatedOnlyFieldListFilter),
        ('container_image', admin.RelatedOnlyFieldListFilter),
        ('group', admin.RelatedOnlyFieldListFilter),
        ('share', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['notification_type', 'message', 'sender']
        }),
        ('Related Objects', {
            'classes': ['collapse'],
            'fields': ['container', 'container_image', 'group', 'share']
        }),
        ('Receivers', {
            'fields': ['receiver_groups']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['container', 'container_image', 'date', 'group', 'message',
                    'notification_type', 'receiver_groups', 'sender', 'share']
        else:
            return []


class ServerAdmin(admin.ModelAdmin):

    """
    Admin model for the `Server` model.
    """

    list_display = ['name', 'internal_ip', 'external_ip', 'is_container_host']
    list_filter = [
        ('container_backend', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'internal_ip', 'external_ip']
        }),
        ('Container Backend Properties', {
            'classes': ['collapse'],
            'fields': ['container_backend', 'container_backend_args']
        })
    ]

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            # TODO: make only readonly if hosts containers
            return ['container_backend', 'external_ip', 'internal_ip']
        else:
            return []


class ShareAdmin(admin.ModelAdmin):

    """
    Admin model for the `Share` model.
    """

    list_display = ['name', 'description', 'owner']
    list_filter = [
        ('owner', admin.RelatedOnlyFieldListFilter),
        ('tags', admin.RelatedOnlyFieldListFilter),
    ]

    fieldsets = [
        ('General Properties', {
            'fields': ['name', 'description', 'tags', 'owner']
        }),
        ('Access Control', {
            'fields': ['access_groups']
        })
    ]
    filter_horizontal = ['tags']

    def get_readonly_fields(self, request, obj=None):
        """
        :inherit.
        """
        if obj:
            return ['name', 'owner']
        else:
            return []


class TagAdmin(admin.ModelAdmin):

    """
    Admin model for the `Tag` model.
    """

    fieldsets = [
        ('General Properties', {
            'fields': ['label']
        })
    ]


class UserAdmin(admin.ModelAdmin):

    """
    Admin model for the `User` model.
    """

    fieldsets = [
        ('General Properties', {
            'fields': ['username', 'is_active', 'is_staff']
        }),
        ('Group Memberships', {
            'classes': ['collapse'],
            'fields': ['groups']
        })
    ]

    readonly_fields = ['username']

    def has_add_permission(self, request):
        """
        :inherit.
        """
        return False


# register the model admins with the site
admin_site = CoreAdminSite(name='ipynbsrv')
admin_site.register(Backend, BackendAdmin)
admin_site.register(CollaborationGroup, CollaborationGroupAdmin)
admin_site.register(ConfigurationVariable, ConfigurationVariableAdmin)
admin_site.register(Container, ContainerAdmin)
admin_site.register(ContainerImage, ContainerImageAdmin)
admin_site.register(ContainerSnapshot, ContainerSnapshotAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(Server, ServerAdmin)
admin_site.register(Share, ShareAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(User, UserAdmin)
