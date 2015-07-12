from collections import Iterator


class ServerSelectionAlgorithm(object):
    '''
    Instances of server selection algorithms are used to decide on which server
    a container should be created.
    '''

    '''
    Returns one server from the input servers.

    If the servers are not of type Iterator, a ValueError should be raised.

    :param servers: An iterator of servers to choose one from (most likely Server.objects.all().iterator())
    '''
    def choose_server(self, servers):
        raise NotImplementedError


class RoundRobin(ServerSelectionAlgorithm):
    '''
    Very primitive round robin server selection algorithm.
    '''

    '''
    Initializes a new RoundRobin instance.

    Note: Each instance is independant of all others.
    '''
    def __init__(self):
        self._last_choosen = 0  # stores the DB ID of the last choosen server object.

    '''
    :inherit
    '''
    def choose_server(self, servers):
        if not isinstance(servers, Iterator):
            raise ValueError("Servers need to be of type collections.Iterator.")

        try:
            first = servers.next()
            current = first
            while current.id <= self._last_choosen:
                current = servers.next()
        except StopIteration:
            if first is None:  # empty iterator
                raise ex
            current = first

        self._last_choosen = current.id
        return current
