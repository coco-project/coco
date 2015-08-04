from django.contrib.auth.models import User, Group
from django.db.models import Q
from django_admin_conf_vars.models import ConfigurationVariable
from ipynbsrv.api.permissions import *
from ipynbsrv.core.helpers import get_server_selection_algorithm
from ipynbsrv.core.models import *
from ipynbsrv.api.serializer import *
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import *
from rest_framework.response import Response

# TODO: check for unique names before creation of objects !


def validate_request_params(required_params, request):
    """
    Validate request parameters.
    """
    params = {}
    for param in required_params:
            if param not in request.data:
                return Response({"error": "Parameters missing.", "required_parameters": required_params })
            params[param] = request.data.get(param)
    return params


@api_view(('GET',))
def api_root(request, format=None):
    """
    API Root
    """
    return Response({'endpoints': {
        'configurationvariables': 'desc',
        'users': 'desc',
        'collaborationgroups': 'desc',
        'backends': 'desc',
        'containers': 'desc',
        'images': 'desc',
        'snapshots': 'desc',
        'servers': 'desc',
        'shares': 'desc',
        'tags': 'desc',
        'notifications': 'desc',
        'notificationlogs': 'desc',
    }})


class ConfigurationVariableList(generics.ListCreateAPIView):
    """
    Get a list of all configuration variables.
    Only visible to authenticated users.
    """

    queryset = ConfigurationVariable.objects.all()
    serializer_class = ConfigurationVariableSerializer
    permission_classes = [IsSuperUser]


class ConfigurationVariableDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get a list of all configuration variables.
    Only visible to authenticated users.
    """

    queryset = ConfigurationVariable.objects.all()
    serializer_class = ConfigurationVariableSerializer
    permission_classes = [IsSuperUser]


class UserList(generics.ListAPIView):
    """
    Get a list of all users (`django.contrib.auth.models.User`).
    Only visible to authenticated users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class UserDetails(generics.RetrieveAPIView):
    """
    Get a list of all users (`django.contrib.auth.models.User`).
    Only visible to authenticated users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class GroupList(generics.ListAPIView):
    """
    Get a list of all groups.
    Only visible to authenticated users.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedAndReadOnly]


class BackendList(generics.ListCreateAPIView):
    """
    Get a list of all the containers.
    """
    queryset = Backend.objects.all()
    serializer_class = BackendSerializer
    permission_classes = [IsSuperUser]


class BackendDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a backend.
    """
    queryset = Backend.objects.all()
    serializer_class = BackendSerializer
    permission_classes = [IsSuperUser]


class CollaborationGroupList(generics.ListCreateAPIView):
    """
    Get a list of all the collaboration groups the user is in.
    """

    serializer_class = CollaborationGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = CollaborationGroup.objects.all()
        else:
            queryset = CollaborationGroup.objects.filter(
                Q(user__id=self.request.user.id)
                | Q(creator=self.request.user.backend_user.id)
                | Q(is_public=True)
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'backend_user'):
            serializer.save(
                creator=self.request.user.backend_user,
                )
        else:
            serializer.save()


class CollaborationGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a collaboration group the user is in.
    """

    serializer_class = CollaborationGroupSerializer
    permission_classes = [IsSuperUserOrIsGroupAdminOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = CollaborationGroup.objects.all()
        else:
            queryset = CollaborationGroup.objects.filter(
                Q(user__id=self.request.user.id)
                | Q(creator=self.request.user.backend_user.id)
                | Q(is_public=True)
            ).distinct()
        return queryset


@api_view(['POST'])
def collaborationgroup_add_members(request, pk):
    """
    Add a list of users to the group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param users list of user ids to add to the group
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # validate all the user_ids first before adding them
    user_list = []
    for user_id in params.get("users"):
        obj = User.objects.filter(id=user_id)
        if not obj:
            return Response({"error": "User not found!", "data": user_id})
        user = obj.first()
        if not user.backend_user:
            return Response({"error": "User has no backend user!", "data": user_id})
        user_list.append(user.backend_user)
    for user in user_list:
        group.add_member(user)

    serializer = CollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_add_admins(request, pk):
    """
    Add a list of users to the group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param users list of user ids to add to the group
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # validate all the user_ids first before adding them
    user_list = []
    for user_id in params.get("users"):
        obj = User.objects.filter(id=user_id)
        if not obj:
            return Response({"error": "User not found!", "data": user_id})
        user = obj.first()
        print(user)
        if not user.backend_user:
            return Response({"error": "User has no backend user!", "data": user_id})
        user_list.append(user.backend_user)
    for user in user_list:
        result = group.add_admin(user)
        if not result:
            return Response({"error": "{} is no member of {}".format(user.username, group.name), "data": user_id})

    serializer = CollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_remove_members(request, pk):
    """
    Remove a list of users from the group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param users list of user ids to remove from the group
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # validate all the user_ids first before adding them
    user_list = []
    for user_id in params.get("users"):
        obj = User.objects.filter(id=user_id)
        if not obj:
            return Response({"error": "User not found!", "data": user_id})
        user = obj.first()
        if not user.backend_user:
            return Response({"error": "User has no backend user!", "data": user_id})
        user_list.append(user.backend_user)
    for user in user_list:
        group.remove_member(user)

    serializer = CollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # target server gets selected by selection algorithm
        server = get_server_selection_algorithm().choose_server(
            Server.objects.all().iterator()
        )
        if hasattr(self.request.user, 'backend_user'):
            serializer.save(
                server=server,
                owner=self.request.user.backend_user
            )
        else:
            serializer.save(
                server=server,
            )


class ContainerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a container.
    """
    serializer_class = ContainerSerializer
    permission_classes = [IsSuperUserOrIsObjectOwner]

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
    Todo: permissions
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
def container_commit(request, pk):
    """
    Create a new image based on this container.

    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the container that needs to be cloned
    :param name:
    :param description:
    :param public:
    """

    required_params = ["name", "description", "public"]
    params = {}
    for param in required_params:
        if param not in request.data:
            return Response({"error": "Parameters missing.", "required_parameters": required_params })
        params[param] = request.data.get(param)

    container = get_container(pk)
    if container:
        image = container.commit(**params)
        print(image)
        serializer = ContainerImageSerializer(image)
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
    permission_classes = [IsSuperUserOrIsObjectOwnerOrReadOnlyIfPublic]

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
    # TODO: permissions

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
    permission_classes = [IsSuperUser]


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a server.
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [IsSuperUser]


class ShareList(generics.ListCreateAPIView):
    """
    Get a list of all the shares.
    """
    serializer_class = ShareSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Share.objects.all()
        else:
            return Share.objects.filter(backend_group__django_group__user=self.request.user)

    def perform_create(self, serializer):
        print("perform create")
        # TODO: handle tags
        # if self.request.POST:

        if hasattr(self.request.user, 'backend_user'):
            serializer.save(
                owner=self.request.user.backend_user,
                )
        else:
            serializer.save()


class ShareDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a share.
    """

    serializer_class = ShareSerializer
    permission_classes = [IsSuperUserOrIsObjectOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Share.objects.all()
        else:
            return Share.objects.filter(backend_group__django_group__user=self.request.user)


@api_view(['POST'])
def share_add_access_groups(request, pk):
    """
    Add a list of collaboration groups to the share.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """
    required_params = ["access_groups"]
    params = validate_request_params(required_params, request)

    obj = Share.objects.filter(id=pk)
    if not obj:
        return Response({"error": "Share not found!", "data": request.data})
    share = obj.first()

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response({"error": "CollaborationGroup not found!", "data": access_group_id})
        access_groups.append(obj.first())
    # add the access groups to the share
    for access_group in access_groups:
        share.add_access_group(access_group)

    serializer = ShareSerializer(share)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def share_remove_access_groups(request, pk):
    """
    Remove a list of collaboration groups from the share.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """
    required_params = ["access_groups"]
    params = validate_request_params(required_params, request)

    obj = Share.objects.filter(id=pk)
    if not obj:
        return Response({"error": "Share not found!", "data": request.data})
    share = obj.first()

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response({"error": "CollaborationGroup not found!", "data": access_group_id})
        access_groups.append(obj.first())
    # add the access groups to the share
    for access_group in access_groups:
        share.remove_access_group(access_group)

    serializer = ShareSerializer(share)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagList(generics.ListCreateAPIView):
    """
    Get a list of all the tags.
    """
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given string,
        by filtering against a `label_text` query parameter in the URL.
        """
        queryset = Tag.objects.all()
        label_text = self.kwargs.get('label_text', None)
        if label_text is not None:
            queryset = queryset.filter(label=label_text)
        return queryset


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
    permission_classes = [IsSuperUserOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(sender=self.request.user)
        return queryset


class NotificationLogList(generics.ListAPIView):
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


@api_view(('GET',))
def notification_types(request, format=None):
    """
    Notification types.
    """
    return Response(Notification.NOTIFICATION_TYPES)
