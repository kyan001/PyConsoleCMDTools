import os


class Path(str):
    """A class that represents a path. It is a subclass of str, so it can be used as a string.

    Attributes:
        path: The path as a string.
        abs: The absolute path as a string.
        basename: The basename of the path.
        ext: The extension of the path.
        stem: The stem of the path.
        parent: The parent directory of the path. Also a Path object.

    Examples:
        filepath: '/path/to/filename.txt'
        basename: 'filename.txt'
        ext: 'txt'
        stem: 'filename'
        parent: '/path/to'
        parent.basename: 'to'
        parent.ext: ''
        parent.stem: 'to'
        parent.parent: '/path'
        +---------------------------+
        |           Path            |
        +----------+----------------+
        |  Parent  |    Basename    |
        |          +----------+-----+
        |          |   Stem   | Ext |
        |          |          |     |
        " /path/to / filename . txt "
        |          |          |     |
        +----------+----------+-----+
    """
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.abs = os.path.abspath(path)

    def __str__(self) -> str:
        return self.abs

    def __repr__(self) -> str:
        return f"Path({self.path!r})"

    @property
    def parent(self) -> Path:
        return Path(os.path.dirname(self.abs))

    @property
    def basename(self) -> str:
        return os.path.basename(self.abs)

    @property
    def ext(self) -> str:
        """Returns the extension of the path without the dot."""
        return os.path.splitext(self.basename)[1].lstrip(".")

    @property
    def stem(self) -> str:
        return os.path.splitext(self.basename)[0]
