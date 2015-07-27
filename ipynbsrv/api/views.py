from django.contrib.auth.models import User, Group
from django.db.models import Q
from ipynbsrv.api.permissions import *
from ipynbsrv.core.models import *
from ipynbsrv.api.serializer import *
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(('GET',))
def api_root(request, format=None):
    """
    API Root
    """
    return Response({
        'endpoint': 'desc',
        'endpoint2': 'desc',
        'endpoint3': 'desc',
    })


class UserList(generics.ListAPIView):
    """
    Get a list of all users (`django.contrib.auth.models.User`).
    Only visible to authenticated users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupList(generics.ListAPIView):
    """
    Get a list of all groups.
    Only visible to authenticated users.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class BackendList(generics.ListCreateAPIView):
    """
    Get a list of all the containers.
    """
    queryset = Backend.objects.all()
    serializer_class = BackendSerializer
    permssion_classes = (IsSuperUser, )


class BackendDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a backend.
    """
    queryset = Backend.objects.all()
    serializer_class = BackendSerializer
    permssion_classes = (IsSuperUser, )


class CollaborationGroupList(generics.ListCreateAPIView):
    """
    Get a list of all the groups the user is in.
    """

    serializer_class = CollaborationGroupSerializer
    permission_classes = (IsBackendUserOrReadOnly, )

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = CollaborationGroup.objects.all()
        else:
            queryset = CollaborationGroup.objects.filter(
                Q(django_group__user__id=self.request.user.id)
                | Q(creator=self.request.user.backend_user.id)
                | Q(admins__id=self.request.user.backend_user.id)
                | Q(public=True)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user.backend_user,
            )


class CollaborationGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a group the user is in.
    """

    serializer_class = CollaborationGroupSerializer
    # TODO: permision does not work yet..
    permssion_classes = (IsGroupAdminOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = CollaborationGroup.objects.all()
        else:
            queryset = CollaborationGroup.objects.filter(
                Q(django_group__user__id=self.request.user.id)
                | Q(creator=self.request.user.backend_user.id)
                | Q(admins__id=self.request.user.backend_user.id)
                | Q(public=True)
            )
        return queryset


class ContainerList(generics.ListCreateAPIView):
    """
    Get a list of all the containers.
    """
    serializer_class = ContainerSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Container.objects.all()
        else:
            queryset = Container.objects.filter(owner=self.request.user.backend_user.id)
        return queryset


class ContainerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a container.
    """
    serializer_class = ContainerSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Container.objects.all()
        else:
            queryset = Container.objects.filter(owner=self.request.user.backend_user.id)
        return queryset


def get_container(pk):
    """
    Get container by pk.
    """
    containers = Container.objects.filter(id=pk)
    if containers:
        return containers.first()
    else:
        return None


@api_view(['POST'])
def container_clone(request, pk):
    """
    Make a clone of the container.
    Todo: show params on OPTIONS call.
    :param pk   pk of the container that needs to be cloned
    :param name
    :param description
    """
    params = {}

    data = request.data

    if not data.get('name'):
        return Response({"error": "please provide name for the clone: {\"name\" : \"some name \"}"})

    params['name'] = data.get('name')

    if data.get('description'):
        params['description'] = data.get('description')

    origin = get_container(pk)
    if origin:
        clone = origin.clone(**params)
        clone.save()
        serializer = ContainerSerializer(clone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})


@api_view(['POST'])
def container_create_snapshot(request, pk):
    """
    Make a snapshot of the container.
    Todo: show params on OPTIONS call.
    :param pk   pk of the container that needs to be cloned
    :param name
    :param description
    """
    params = {}

    data = request.data

    if not data.get('name'):
        return Response({"error": "please provide name for the clone: {\"name\" : \"some name \"}"})

    params['name'] = data.get('name')

    if data.get('description'):
        params['description'] = data.get('description')

    origin = get_container(pk)
    if origin:
        snapshot = origin.create_snapshot(**params)
        snapshot.save()
        serializer = ContainerSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "pk": pk})


@api_view(['GET'])
def container_clones(request, pk):
    container = get_container(pk)
    if container:
        clones = container.get_clones()
        serializer = ContainerSerializer(clones, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "pk": pk})


@api_view(['POST'])
def container_restart(request, pk):
    """
    Restart the container.
    :param pk   pk of the container that needs to be cloned
    """
    containers = Container.objects.filter(id=pk)

    if containers:
        container = containers.first()
        container.restart()
        return Response({"message": "container rebooting"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})


@api_view(['POST'])
def container_resume(request, pk):
    """
    Resume the container.
    :param pk   pk of the container that needs to be cloned
    """
    containers = Container.objects.filter(id=pk)

    if containers:
        container = containers.first()
        container.resume()
        return Response({"message": "container resuming"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})
    pass


@api_view(['POST'])
def container_start(request, pk):
    """
    Start the container.
    :param pk   pk of the container that needs to be cloned
    """
    containers = Container.objects.filter(id=pk)

    if containers:
        container = containers.first()
        container.start()
        return Response({"message": "container booting"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})
    pass


@api_view(['POST'])
def container_stop(request, pk):
    """
    Stop the container.
    :param pk   pk of the container that needs to be cloned
    """
    containers = Container.objects.filter(id=pk)

    if containers:
        container = containers.first()
        container.stop()
        return Response({"message": "container stopping"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})
    pass


@api_view(['POST'])
def container_suspend(request, pk):
    """
    Suspend the container.
    :param pk   pk of the container that needs to be cloned
    """
    containers = Container.objects.filter(id=pk)

    if containers:
        container = containers.first()
        container.suspend()
        return Response({"message": "container suspending"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})
    pass


class ContainerImageList(generics.ListCreateAPIView):
    """
    Get a list of all the container images.
    """
    serializer_class = ContainerImageSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = ContainerImage.objects.all()
        else:
            queryset = ContainerImage.objects.filter(
                Q(owner=self.request.user) | Q(is_public=True)
            )
        return queryset


class ContainerImageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a container image.
    """
    serializer_class = ContainerImageSerializer
    permssion_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = ContainerImage.objects.all()
        else:
            queryset = ContainerImage.objects.filter(
                Q(owner=self.request.user) | Q(is_public=True)
            )
        return queryset


class ContainerSnapshotList(generics.ListCreateAPIView):
    """
    Get a list of all the container snapshots.
    """
    serializer_class = ContainerSnapshotSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = ContainerSnapshot.objects.all()
        else:
            queryset = ContainerSnapshot.objects.filter(
                container__owner=self.request.user.backend_user
            )
            return queryset


class ContainerSnapshotDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a container snapshot.
    """
    serializer_class = ContainerSnapshotSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = ContainerSnapshot.objects.all()
        else:
            queryset = ContainerSnapshot.objects.filter(
                container__owner=self.request.user.backend_user
            )
            return queryset


class ServerList(generics.ListCreateAPIView):
    """
    Get a list of all the servers.
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a server.
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer


class ShareList(generics.ListCreateAPIView):
    """
    Get a list of all the shares.
    """
    serializer_class = ShareSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Share.objects.all()
        else:
            return Share.objects.filter(
                Q(owner=self.request.user.backend_user)
                | Q(backend_group__django_group__user=self.request.user)
                )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.backend_user)


class ShareDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a share.
    """

    serializer_class = ShareSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Share.objects.all()
        else:
            return Share.objects.filter(
                Q(owner=self.request.user.backend_user)
                | Q(backend_group__django_group__user=self.request.user)
                )


class TagList(generics.ListCreateAPIView):
    """
    Get a list of all the tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class NotificationList(generics.ListCreateAPIView):
    """
    Get a list of all the notifications.
    """

    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(sender=self.request.user)
        return queryset


class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a notification.
    """

    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(sender=self.request.user)
        return queryset


class NotificationLogList(generics.ListCreateAPIView):
    """
    Get a list of all the notification logs.
    """

    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return NotificationLog.objects.all()
        else:
            return NotificationLog.objects.filter(user=self.request.user.backend_user)


class NotificationLogDetail (generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a notification.
    """
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return NotificationLog.objects.all()
        else:
            return NotificationLog.objects.filter(user=self.request.user.backend_user)
