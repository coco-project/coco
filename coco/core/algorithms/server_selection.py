from collections import Iterator


class ServerSelectionAlgorithm(object):

    """
    Algorithm class to be used to decide on which server a container should be created.
    """

    def choose_server(self, servers):
        """
        Choose one server from the input servers.

        If the servers are not of type Iterator, a ValueError should be raised.

        :param servers: An iterator of servers to choose one from (most likely Server.objects.all().iterator())
        """
        raise NotImplementedError


class RoundRobin(ServerSelectionAlgorithm):

    """
    Very primitive round robin server selection algorithm.
    """

    def __init__(self):
        """
        Initialize a new RoundRobin instance.

        Note: All instances are independant of each other.
        """
        self._last_choosen = 0  # stores the DB ID of the last choosen server object.

    def choose_server(self, servers):
        """
        :inherit.
        """
        if not isinstance(servers, Iterator):
            raise ValueError("Servers need to be of type collections.Iterator.")

        try:
            first = servers.next()
            current = first
            while current.id <= self._last_choosen:
                current = servers.next()
        except StopIteration as ex:
            if first is None:  # empty iterator
                raise ex  # TODO: backends error type
            current = first

        self._last_choosen = current.id
        return current
