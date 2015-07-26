from rest_framework import serializers
from ipynbsrv.core.models import *
from ipynbsrv.core import settings
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = User
        fields = ('id', 'username', )
        read_only_fields = ('id', 'username', )


class GroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    user_set = UserSerializer(many=True,read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'user_set')
        read_only_fields = ('user_set', )


class BackendSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Backend


class CollaborationGroupSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """
    django_group = GroupSerializer(many=False)

    class Meta:
        model = CollaborationGroup
        fields = ('id', 'django_group', 'creator', 'admins', 'public')
        read_only_fields = ('creator', )

    def create(self, validated_data):
        """
        Create object from serialized data passed through from views.py.
        """
        # django_group need to be created first because the foreign key is in
        # the CollaborationGroup model
        group_data = validated_data.pop('django_group')
        group = Group.objects.create(**group_data)
        # add creator to group
        group.user_set.add(validated_data.get('creator').django_user)
        # get group admins
        admins = validated_data.pop('admins')
        # create collaboration group
        collab_group = CollaborationGroup.objects.create(
            django_group=group,
            **validated_data
            )
        # set admins and add them as group members
        for admin in admins:
            collab_group.admins.add(admin)
            #group.user_set.add(admin.django_user)
        return collab_group


class ContainerSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Container


class ContainerImageSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = ContainerImage


class ContainerSnapshotSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = ContainerSnapshot


class ServerSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Server


class ShareSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Share
        fields = ('id', 'name', 'description', 'owner', 'tags', 'access_groups')


class TagSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Tag


class NotificationSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = Notification


class NotificationLogSerializer(serializers.ModelSerializer):
    """
    Todo: write doc.
    """

    class Meta:
        model = NotificationLog
