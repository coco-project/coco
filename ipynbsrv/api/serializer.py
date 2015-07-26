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

    def set_admins(self, admins, collab_group, django_group):
        """
        Set the admins on the collaboration group, 
        and add them as members of the django_group.
        """
        for admin in admins:
            collab_group.admins.add(admin)
            django_group.user_set.add(admin.django_user)

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
        self.set_admins(admins, collab_group, group)
        return collab_group

    def update(self, instance, validated_data):
        group_data = validated_data.pop('django_group')
        django_group = instance.django_group
        for attr, value in group_data.items():
            setattr(django_group, attr, value)
        django_group.save()

        # always keep creator and admins in the user set
        admins = validated_data.pop('admins')
        self.set_admins(admins, instance, django_group)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


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
        print("create share")
        name = validated_data.get('name')
        group = Group.objects.create(name=name)
        group.save()
        backend_group = BackendGroup(
            django_group=group,
            backend_id=BackendGroup.generate_internal_guid(),
            backend_pk=name
        )
        backend_group.save()

        print(validated_data)
        tags = validated_data.pop("tags")
        access_groups = validated_data.pop("access_groups")

        # create share
        share = Share.objects.create(
            backend_group=backend_group,
            **validated_data
            )
        self.set_tags(tags, share)
        self.set_access_groups(access_groups, share)
        return share


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
