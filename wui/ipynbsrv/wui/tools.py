import os.path


class Filesystem(object):
    """
    Helper class to work with the filesystem.
    """
    @staticmethod
    def ensure_directory(directory, recursive=False):
        parent = os.path.abspath(os.path.join(directory, os.pardir))
        if recursive and not os.path.exists(parent):
            Filesystem.ensure_directory(parent)
        if not os.path.exists(directory):
            return os.makedirs(directory)
