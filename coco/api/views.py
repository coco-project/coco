from coco.api.permissions import *
from coco.core.helpers import get_server_selection_algorithm
from coco.core.models import *
from coco.api.serializer import *
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django_admin_conf_vars.models import ConfigurationVariable
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
    available_endpoints = {}
    available_endpoints['users'] = {
        '': 'Get a list of all users.',
        '{id}': 'Get details about a user.'
    }
    available_endpoints['collaborationgroups'] = {
        '': 'Get a list of all collaborationgroups.',
        '{id}': {
            '': 'Get details about a collaborationgroup.',
            'add_members': 'Add members to a collaborationgroup.',
            'remove_members': 'Remove members from a collaborationgroup.',
            'add_admins': 'Add admins to a collaborationgroup.',
            'remove_admins': 'Remove admins from a collaborationgroup.',
            'join': 'Join a public collaborationgroup.',
            'leave': 'Leave a collaborationgroup.'
        }
    }
    available_endpoints['containers'] = {
        '': 'Get a list of all containers available to your user.',
        'images': {
            '': 'Get a list of all container images available to your user.',
            '{id}': {
                'add_access_groups': 'Add access_groups to the share.',
                'remove_access_groups': 'Remove access_groups from the share.'
            }
        },
        'snapshots': 'Get a list of all container snapshots available to your user.',
        '{id}': {
            '': 'Get details about a container.',
            'commit': 'Create an image from the container.',
            'clone': 'Clone the container.',
            'clones': 'Get a list of all clones of the container',
            'create_snapshot': 'Create a snapshot of the container.',
            'restore_snapshot': 'Restore a snapshot of the container.',
            'restart': 'Restart the container.',
            'resume': 'Resume the container.',
            'start': 'Start the container.',
            'stop': 'Stop the container.',
            'suspend': 'Suspend the container.'
        }
    }
    available_endpoints['shares'] = {
        '': 'Get a list of all available shares.',
        '{id}': {
            '': 'Get details about a share.',
            'add_access_groups': 'Add access_groups to the share.',
            'remove_access_groups': 'Remove access_groups from the share.'
        }
    }
    available_endpoints['tags'] = {
        '': 'Get a list of all available tags.',
        '{id}': 'Get details about a tag.'
    }
    available_endpoints['notifications'] = {
        '': 'Get a list of all available notifications.',
        '{id}': 'Get details about a notification.'
    }
    available_endpoints['notificationlogs'] = {
        '': 'Get a list of all available notificationlogs.',
        '{id}': 'Get details about a notificationlog.',
        'unread': 'Get all new notificationlogs.',
        'mark_all_as_read': 'Mark all your notificationlogs as read.'
    }
    available_endpoints['notificationtypes'] = 'Get a list of all available notificationtypes.'

    # additional endpoints for superusers only
    if request.user.is_superuser:
        available_endpoints['configurationvariables'] = {
            '': 'Get a list of all available configurationvariables.',
            '{id}': 'Get details about a configurationvariable.'
        }
        available_endpoints['backends'] = {
            '': 'Get a list of all available backends.',
            '{id}': 'Get details about a backend.'
        }
        available_endpoints['servers'] = {
            '': 'Get a list of all available servers.',
            '{id}': 'Get details about a server.'
        }

    return Response(available_endpoints)


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
    permission_classes = [IsSuperUserOrAuthenticatedAndReadOnly]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details about a user (`django.contrib.auth.models.User`).
    Only visible to authenticated users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOrAuthenticatedAndReadOnly]


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

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatCollaborationGroupSerializer
        return NestedCollaborationGroupSerializer

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
    permission_classes = [CollaborationGroupDetailPermission]
    queryset = CollaborationGroup.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatCollaborationGroupSerializer
        return NestedCollaborationGroupSerializer


@api_view(['POST'])
def collaborationgroup_add_members(request, pk):
    """
    Add a list of users to the group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param POST.users list of user ids, i.e. { "users": [1,2,3]}
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # check permissions
    validate_object_permission(CollaborationGroupDetailPermission, request, group)

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
        result = group.add_user(user)
        if not result:
            return Response({"error": "{} is already member of {}".format(user.username, group.name), "data": user.id})

    serializer = NestedCollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_add_admins(request, pk):
    """
    Make a list of users to group admins.
    Only users that are already members of the group will be added as admins.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param POST.users list of user ids, i.e. { "users": [1,2,3]}
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # check permissions
    validate_object_permission(CollaborationGroupDetailPermission, request, group)

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
        result = group.add_admin(user)
        if not result:
            return Response({"error": "{} is already admin of {}".format(user.username, group.name), "data": user.id})

    serializer = NestedCollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_remove_admins(request, pk):
    """
    Remove a list of users from group admins.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param POST.users list of user ids, i.e. { "users": [1,2,3]}
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # check permissions
    validate_object_permission(CollaborationGroupDetailPermission, request, group)

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
        result = group.remove_admin(user)
        if not result:
            return Response({"error": "{} is no admin of {}".format(user.username, group.name), "data": user.id})

    serializer = NestedCollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_remove_members(request, pk):
    """
    Remove a list of users from the group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    :param POST.users list of user ids, i.e. { "users": [1,2,3]}
    """
    required_params = ["users"]
    params = validate_request_params(required_params, request)

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    # check permissions
    validate_object_permission(CollaborationGroupDetailPermission, request, group)

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
        result = group.remove_member(user)
        if not result:
            return Response({"error": "{} is no member of {}".format(user.username, group.name), "data": user.id})

    serializer = NestedCollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_join(request, pk):
    """
    Join a group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    if not group.is_public:
        return Response({"error": "{} could not be added to {}. Group not public.".format(request.user.username, group.name)})

    result = group.add_user(request.user.backend_user)
    if not result:
        return Response({"error": "{} could not be added to {}".format(request.user.username, group.name)})

    serializer = NestedCollaborationGroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def collaborationgroup_leave(request, pk):
    """
    Leave a group.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """

    obj = CollaborationGroup.objects.filter(id=pk)
    if not obj:
        return Response({"error": "CollaborationGroup not found!", "data": request.data})
    group = obj.first()

    result = group.remove_member(request.user.backend_user)
    if not result:
        return Response({"error": "{} could not be removed from {}. Not a member or creator.".format(request.user.username, group.name)})

    serializer = NestedCollaborationGroupSerializer(group)
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
    permission_classes = [ContainerDetailPermission]
    queryset = Container.objects.all()


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

    # validate permissions
    validate_object_permission(ContainerDetailPermission, request, origin)

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

    # validate permissions
    validate_object_permission(ContainerDetailPermission, request, container)

    if container:
        image = container.commit(**params)

        serializer = ContainerImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Container not found!", "data": data})


@api_view(['POST'])
def container_create_snapshot(request, pk):
    """
    Create a snapshot of the container.
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

    # validate permissions
    validate_object_permission(ContainerDetailPermission, request, origin)

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

    # validate permissions
    validate_object_permission(ContainerDetailPermission, request, container)

    if container:
        clones = container.get_clones()
        serializer = ContainerSerializer(clones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
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

        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)

        container.restart()
        return Response({"message": "container rebooting"}, status=status.HTTP_200_OK)
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
        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)
        container.resume()
        return Response({"message": "container resuming"}, status=status.HTTP_200_OK)
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
        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)
        container.start()
        return Response({"message": "container booting"}, status=status.HTTP_200_OK)
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
        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)
        container.stop()
        return Response({"message": "container stopping"}, status=status.HTTP_200_OK)
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
        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)
        container.suspend()
        return Response({"message": "container suspending"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Container not found!", "data": data})
    pass


class ContainerImageList(generics.ListCreateAPIView):
    """
    Get a list of all the container images.
    """

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatContainerImageSerializer
        return ContainerImageSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = ContainerImage.objects.all()
        else:
            collab_group = None
            if hasattr(self.request.user, 'backend_user'):
                collab_group = self.request.user.backend_user.get_collaboration_group()
            if collab_group:
                queryset = ContainerImage.objects.filter(
                    Q(is_internal=False) & (Q(owner=self.request.user) | Q(is_public=True) | Q(access_groups__user=self.request.user))
                ).distinct()
            else:
                queryset = ContainerImage.objects.filter(
                    Q(is_internal=False) & (Q(owner=self.request.user) | Q(is_public=True))
                ).distinct()
        return queryset


class ContainerImageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get details of a container image.
    """
    serializer_class = ContainerImageSerializer
    permission_classes = [ContainerImageDetailPermission]
    queryset = ContainerImage.objects.all()


@api_view(['POST'])
def image_add_access_groups(request, pk):
    """
    Add a list of collaboration groups to the image.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """
    required_params = ["access_groups"]
    params = validate_request_params(required_params, request)

    obj = ContainerImage.objects.filter(id=pk)
    if not obj:
        return Response({"error": "Image not found!", "data": request.data})
    image = obj.first()

    # validate permissions
    validate_object_permission(ContainerImageDetailPermission, request, image)

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response(
                {"error": "CollaborationGroup not found!", "data": access_group_id},
                status=status.HTTP_404_NOT_FOUND
                )
        access_groups.append(obj.first())

    added_groups = []
    # add the access groups to the share
    for access_group in access_groups:
        if image.add_access_group(access_group):
            added_groups.append((access_group.id, access_group.name))

    return Response({
        "detail": "Groups added successfully",
        "groups": added_groups,
        "count": len(added_groups)
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def image_remove_access_groups(request, pk):
    """
    Remove a list of collaboration groups from the image.
    Todo: show params on OPTIONS call.
    Todo: permissions
    :param pk   pk of the collaboration group
    """
    required_params = ["access_groups"]
    params = validate_request_params(required_params, request)
    obj = ContainerImage.objects.filter(id=pk)
    if not obj:
        return Response({"error": "Image not found!", "data": request.data})
    image = obj.first()

    # validate permissions
    validate_object_permission(ContainerImageDetailPermission, request, image)

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response(
                {"error": "CollaborationGroup not found!", "data": access_group_id},
                status=status.HTTP_404_NOT_FOUND
                )
        access_groups.append(obj.first())

    removed_groups = []
    # add the access groups to the share
    for access_group in access_groups:
        if image.remove_access_group(access_group):
            removed_groups.append((access_group.id, access_group.name))

    return Response({
        "detail": "Groups removed successfully",
        "groups": removed_groups,
        "count": len(removed_groups)
        },
        status=status.HTTP_200_OK
    )


class ContainerSnapshotsList(generics.ListAPIView):
    """
    Get a list of all snapshots for a specific container.
    """
    serializer_class = ContainerSnapshotSerializer

    def get_queryset(self):
        # get pk of container from url
        pk = self.kwargs['pk']
        if self.request.user.is_superuser:
            queryset = ContainerSnapshot.objects.all().filter(container__id=pk)
        else:
            queryset = ContainerSnapshot.objects.filter(
                container__owner=self.request.user.backend_user
            ).filter(container=pk)
            return queryset


class ContainerSnapshotList(generics.ListAPIView):
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
    permission_classes = [ContainerSnapshotDetailPermission]
    queryset = ContainerSnapshot.objects.all()


@api_view(['POST'])
def container_snapshot_restore(request, pk):
    """
    Restore a snapshot of the container.
    Todo: show params on OPTIONS call.
    :param pk   pk of the container that needs to be cloned
    """
    snapshots = ContainerSnapshot.objects.filter(id=pk)
    if snapshots:
        s = snapshots.first()
        container = s.container
        # validate permissions
        validate_object_permission(ContainerDetailPermission, request, container)
        s.restore()
        serializer = ContainerSerializer(container)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Snapshot not found!", "pk": pk})


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

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatShareSerializer
        return NestedShareSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Share.objects.all()
        else:
            return Share.objects.filter(
                backend_group__django_group__user=self.request.user
                )

    def perform_create(self, serializer):

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

    permission_classes = [ShareDetailPermissions]
    queryset = Share.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatShareSerializer
        return NestedShareSerializer


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

    # validate permissions
    validate_object_permission(ShareDetailPermissions, request, share)

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response(
                {"error": "CollaborationGroup not found!", "data": access_group_id},
                status=status.HTTP_404_NOT_FOUND
                )
        access_groups.append(obj.first())

    added_groups = []
    # add the access groups to the share
    for access_group in access_groups:
        if share.add_access_group(access_group):
            added_groups.append((access_group.id, access_group.name))

    return Response({
        "detail": "Groups added successfully",
        "groups": added_groups,
        "count": len(added_groups)
        },
        status=status.HTTP_200_OK
    )


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

    # validate permissions
    validate_object_permission(ShareDetailPermissions, request, share)

    # validate all the access_groups first before adding them
    access_groups = []
    for access_group_id in params.get("access_groups"):
        obj = CollaborationGroup.objects.filter(id=access_group_id)
        if not obj:
            return Response(
                {"error": "CollaborationGroup not found!", "data": access_group_id},
                status=status.HTTP_404_NOT_FOUND
                )
        access_groups.append(obj.first())

    removed_groups = []
    # add the access groups to the share
    for access_group in access_groups:
        if share.remove_access_group(access_group):
            removed_groups.append((access_group.id, access_group.name))

    return Response({
        "detail": "Groups removed successfully",
        "groups": removed_groups,
        "count": len(removed_groups)
        },
        status=status.HTTP_200_OK
    )


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
            queryset = queryset.filter(label__iexact=label_text)
        return queryset


class TagDetail(generics.RetrieveDestroyAPIView):
    """
    Get details of a tag.
    """

    permission_classes = [IsSuperUserOrAuthenticatedAndReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class NotificationList(generics.ListCreateAPIView):
    """
    Get a list of all the notifications.
    """

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatNotificationSerializer
        return NestedNotificationSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Notification.objects.all()
        else:
            queryset = Notification.objects.filter(sender=self.request.user)
        return queryset

    def perform_create(self, serializer):
        sender = serializer.context.get('request').POST.getlist('sender')
        # check if sender has been provided in POST data
        sender_provided = filter(None, sender)

        if self.request.user.is_superuser and sender_provided:
            serializer.save()
        else:
            serializer.save(sender=self.request.user)


class NotificationDetail(generics.RetrieveDestroyAPIView):
    """
    Get details of a notification.
    """

    permission_classes = [NotificationDetailPermission]
    queryset = Notification.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH', 'POST', 'PUT']:
            return FlatNotificationSerializer
        return NestedNotificationSerializer


class NotificationLogList(generics.ListAPIView):
    """
    Get a list of all the notification logs.
    """

    serializer_class = NotificationLogSerializer

    def get_serializer_class(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return SuperUserNotificationLogSerializer
        return NotificationLogSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return NotificationLog.objects.all().order_by('-notification__date')
        else:
            return NotificationLog.objects.filter(user=self.request.user.backend_user) \
                                          .filter(in_use=True) \
                                          .order_by('-notification__date')


class NotificationLogUnreadList(generics.ListAPIView):
    """
    Get a list of all the notification logs.
    """

    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        return NotificationLog.objects.filter(user=self.request.user.backend_user) \
                                          .filter(in_use=True).filter(read=False) \
                                          .order_by('-notification__date')


class NotificationLogDetail(generics.RetrieveUpdateAPIView):
    """
    Get details of a notification.
    """
    serializer_class = NotificationLogSerializer
    permission_classes = [NotificationLogDetailPermission]
    queryset = NotificationLog.objects.all()


@api_view(('POST',))
def notificationlogs_mark_all_as_read(request):
    """
    Mark all notificationlogs of a user as read.
    """
    notifications = NotificationLog.objects.filter(user=request.user.backend_user)
    count = 0
    for n in notifications:
        if not n.read:
            n.read=True
            n.save()
            count += 1
    return Response({"detail": "{} NotificationLog objects marked as read.".format(count), "count": count})


@api_view(('GET',))
def notification_types(request):
    """
    Notification types.
    """
    return Response(Notification.NOTIFICATION_TYPES)
