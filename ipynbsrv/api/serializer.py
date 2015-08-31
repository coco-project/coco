from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django_admin_conf_vars.models import ConfigurationVariable
from ipynbsrv.core import settings
from ipynbsrv.core.models import *
from rest_framework import serializers


class CurrentBackendUserDefault(object):
    """
    A default class that can be used to represent the current backend user.
    In order to use this, the 'request' must have been provided
    as part of the context dictionary when instantiating the serializer
    and the user needs to have a backend user.

    Based on `rest_framework.serializers.CurrentUserDefault`.
    See the django-rest-framework documentation for more info:
    http://www.django-rest-framework.org/api-guide/validators/#currentuserdefault
    """
    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user

    def __call__(self):
        return self.user.backend_user

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)


class ConfigurationVariableSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = ConfigurationVariable


class FlatCollaborationGroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)

    class Meta:
        model = CollaborationGroup
        fields = ('id', 'name', 'creator', 'member_count', 'admins', 'is_public', 'is_single_user_group')
        read_only_fields = ('admins', 'is_single_user_group')


class FlatBackendUserSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    collab_group = FlatCollaborationGroupSerializer(source='get_collaboration_group')

    class Meta:
        model = BackendUser
        fields = ('id', 'collab_group',)


class UserSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    backend_user = FlatBackendUserSerializer(read_only=True, many=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'backend_user', 'is_active', 'is_staff')
        read_only_fields = ('id', 'username', 'backend_user', 'is_staff')


class NestedBackendUserSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    username = serializers.CharField(source='get_username')
    django_user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = BackendUser
        fields = ('id', 'username', 'django_user')


class GroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    user_set = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'user_set')


class BackendGroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = BackendGroup


class BackendSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    arguments = serializers.CharField(required=False)

    class Meta:
        model = Backend


class NestedCollaborationGroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    member_count = serializers.IntegerField(source='get_member_count', read_only=True)
    members = NestedBackendUserSerializer(source='get_members', read_only=True, many=True)
    creator = NestedBackendUserSerializer(many=False, read_only=True)

    class Meta:
        model = CollaborationGroup
        fields = ('id', 'name', 'creator', 'members', 'member_count', 'admins', 'is_public', 'is_single_user_group')
        read_only_fields = ('admins', 'is_single_user_group')


class ServerSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    is_container_host = serializers.BooleanField(read_only=True)

    class Meta:
        model = Server


class PortMappingSerializer(serializers.ModelSerializer):
    """

    """
    is_protected_mapping = serializers.BooleanField(read_only=True)

    class Meta:
        model = PortMapping


class FlatContainerSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    class Meta:
        model = Container


class ContainerSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    Although server can be set on creation, it will be ignored.
    Server is set through the server selection algorithm set in the conf module.
    """
    backend_name = serializers.CharField(read_only=True, source='get_backend_name')
    backend_base_url = serializers.CharField(read_only=True, source='get_backend_base_url')
    friendly_name = serializers.CharField(read_only=True, source='get_friendly_name')
    is_clone = serializers.BooleanField(read_only=True)
    is_image_based = serializers.BooleanField(read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_suspended = serializers.BooleanField(read_only=True)
    has_clones = serializers.BooleanField(read_only=True)
    port_mappings = PortMappingSerializer(
        many=True,
        read_only=True
        )

    owner = serializers.HiddenField(
        default=CurrentBackendUserDefault()
    )

    # set dummy default, will be overriden on creation anyway
    server = ServerSerializer(
        read_only=True,
        default=randint(0, 1000)
    )
    # set dummy default, will be overriden on creation anyway
    backend_pk = serializers.CharField(
        default=randint(0, 1000),
        read_only=True
    )

    class Meta:
        model = Container


class ContainerImageSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    friendly_name = serializers.CharField(read_only=True, source='get_friendly_name')
    owner = UserSerializer(many=False)
    access_groups = FlatCollaborationGroupSerializer(many=True, read_only=True)

    class Meta:
        model = ContainerImage


class FlatContainerImageSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    friendly_name = serializers.CharField(read_only=True, source='get_friendly_name')
    access_groups = FlatCollaborationGroupSerializer(many=True, read_only=True)

    class Meta:
        model = ContainerImage


class ContainerSnapshotSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    friendly_name = serializers.CharField(read_only=True, source='get_friendly_name')
    container = FlatContainerSerializer(read_only=True, many=False)

    class Meta:
        model = ContainerSnapshot


class TagSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Tag


class NestedShareSerializer(serializers.ModelSerializer):
    """
    Nested ShareSerializer where all related fields are verbose.
    Used for read_only.
    """
    tags = TagSerializer(many=True, read_only=True)
    members = NestedBackendUserSerializer(source='get_members', many=True, read_only=True)
    access_groups = FlatCollaborationGroupSerializer(many=True, read_only=True)
    owner = NestedBackendUserSerializer(many=False, read_only=True)

    class Meta:
        model = Share


class FlatShareSerializer(serializers.ModelSerializer):
    """
    Flat ShareSerializer where all related fields are only represented by their id.
    Used for write actions.
    """

    # make access_groups optional
    # access_groups = serializers.ListField(
    #     child=serializers.IntegerField(),
    #     required=False
    # )
    # make tags optional
    # tags = serializers.ListField(
    #     child=serializers.IntegerField(),
    #     required=False
    # )
    # owner = serializers.HiddenField(
    #     default=CurrentBackendUserDefault()
    # )

    class Meta:
        model = Share
        fields = ('id', 'name', 'description', 'owner', 'tags', 'access_groups')

    def set_tags(self, tags, instance):
        for tag in tags:
            instance.tags.add(tag)

    def set_access_groups(self, access_groups, instance):
        for group in access_groups:
            instance.access_groups.add(group)

    def create(self, validated_data):
        """
        Create object from serialized data passed through from views.py.
        """
        # django_group need to be created first because the foreign key is in
        # the CollaborationGroup model
        name = settings.SHARE_GROUP_PREFIX + validated_data.get('name')
        group = Group.objects.create(name=name)
        group.save()
        backend_group = BackendGroup(
            django_group=group,
            backend_pk=name
        )
        backend_group.save()

        tags = access_groups = []
        if 'tags' in validated_data:
            tags = validated_data.pop("tags")
        if 'access_groups' in validated_data:
            access_groups = validated_data.pop("access_groups")

        # create share
        share = Share.objects.create(
            backend_group=backend_group,
            **validated_data
            )
        if tags:
            self.set_tags(tags, share)
        if access_groups:
            self.set_access_groups(access_groups, share)
        return share


class NestedNotificationSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES, default='miscellaneous')
    sender = UserSerializer(many=False)
    url_slug = serializers.CharField(source='get_related_object_url', read_only=True)
    has_related_object = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        read_only_fields = ('date', )


class FlatNotificationSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Notification
        read_only_fields = ('date', )


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    notification = NestedNotificationSerializer(read_only=True, many=False)

    class Meta:
        model = NotificationLog
        fields = ('id', 'notification', 'read', 'user')
        read_only_fields = ('id', 'notification', 'user')


class SuperUserNotificationLogSerializer(serializers.ModelSerializer):
    """
    Special NotificationLogSerializer for superusers, that additionally shows the in_use field.
    """

    notification = NestedNotificationSerializer(read_only=True, many=False)

    class Meta:
        model = NotificationLog
        fields = ('id', 'notification', 'in_use', 'read', 'user')
        read_only_fields = ('id', 'notification', 'in_use', 'user')
