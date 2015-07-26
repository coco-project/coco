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

    class Meta:
        model = CollaborationGroup
        fields = ('id', 'creator', 'admins', 'public')
        read_only_fields = ('creator', )


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
