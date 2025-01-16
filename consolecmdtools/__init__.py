# -*- coding: utf-8 -*-
import os
import sys
import platform
import urllib.request
import urllib.parse
import json
import io
import pathlib
import typing
import shutil
# !! some imports are lazy-loaded

import consoleiotools as cit

from .path import Path


__version__ = '6.6.3'


def banner(text: str) -> str:
    """Generate a banner of 3 lines"""
    FILLER = "#"
    text = text.strip()
    middle_line = FILLER + text.center(int(len(text) / 0.618)) + FILLER
    top_line = bottom_line = FILLER * len(middle_line)
    return "\n".join([top_line, middle_line, bottom_line])


def md5(target: str | bytes, force_text: bool = False) -> str:
    """Generate MD5 hash for bytes, str, int, file, etc."""
    import hashlib

    if not target:
        return ""
    if not force_text and os.path.isfile(target):  # if target is a file
        with open(target, 'rb') as f:
            content = f.read().replace(os.linesep.encode(), b"\n")  # universal newline
            return hashlib.md5(content).hexdigest()
    if not isinstance(target, bytes):  # the input of hashlib.md5() should be type of bytes
        target = str(target).encode()
    return hashlib.md5(target).hexdigest()


def crc32(target: str | bytes, force_text: bool = False) -> int:
    """Generate CRC32 hash for bytes, str, int, file, etc."""
    import binascii

    if not target:
        return 0
    if not force_text and os.path.isfile(target):  # if target is a file
        with open(target, 'rb') as f:
            content = f.read().replace(os.linesep.encode(), b"\n")  # universal newline
            return binascii.crc32(content)
    if not isinstance(target, bytes):  # if target is str/int/float, the input of binascii.crc32() should be type of bytes
        target = str(target).encode()
    return binascii.crc32(target)


def main_color(source: str, scale: int = 200, triplet: str = "rgb", is_url: bool = False) -> str | tuple[int, int, int] | None:
    """Get a representative color from the source-pointed image

    Imports:
        colorsys: Shipped with python.
        PIL: Use `pip install pillow` or install by package manager (apt, apk, etc).

    Args:
        source (str): The URL of the image, or the filepath.
        scale (int): The size of generated image thumbnail.
        triplet (str): The return value format. `rgb` for RGB triplet: (255, 255, 255), and `hex` for HEX triplet: '#FFFFFF'.
        is_url (bool): The source should be downloaded or not.

    Returns:
        str: The main color of the source image in RGB or HEX format.
    """
    import colorsys
    try:
        from PIL import Image
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError("Install pillow (`pip install pillow`) to use PIL.") from e

    if not source:
        return None
    if is_url:
        img_buffer = io.BytesIO(read_url(source))
        img = Image.open(img_buffer).convert("RGBA")
    else:  # source is an image file
        img = Image.open(source).convert("RGBA")
    img.thumbnail((scale, scale))
    statistics: dict = {
        "r": 0,
        "g": 0,
        "b": 0,
        "coef": 0
    }
    for count, (r, g, b, a) in img.getcolors(img.size[0] * img.size[1]):  # get each color used in image with its count, maxcolors = the size of the image.
        _h, s, _v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        saturation = s * 255  # extend the range from 0~1 to 0~255
        coefficient: float = (saturation * count * a) or 0.01  # get how important this color is. Should not be 0.
        statistics["r"] += coefficient * r  # raise the importance of red of this image.
        statistics["g"] += coefficient * g
        statistics["b"] += coefficient * b
        statistics["coef"] += coefficient
    color = (
        int(statistics["r"] / statistics["coef"]),  # normalize to 0~255
        int(statistics["g"] / statistics["coef"]),
        int(statistics["b"] / statistics["coef"])
    )
    if triplet.lower() == "hex":
        return "#%0.2X%0.2X%0.2X" % color
    else:
        return color


def clear_screen():
    """Clear the console screen"""
    if platform.system() == "Windows":  # Windows
        os.system("cls")
    elif platform.system() == "Linux":  # Linux
        os.system("clear")
    elif platform.system() == "Darwin":  # macOS
        os.system("clear")
    else:  # Other OS
        os.system("clear")


def get_py_cmd() -> str:
    """Get OS's python command"""
    for cmd in ("py", "python3", "python"):
        if is_cmd_exist(cmd):
            return cmd
    return sys.executable


def run_cmd(cmd: str) -> bool:
    """Run command and show if success or failed

    Args:
        cmd (str): The command.
    Returns:
        bool: Does this command run successfully
    """
    SUCCESS_CODE = 0
    cit.echo(cmd, pre="command")
    is_success = (os.system(cmd) == SUCCESS_CODE)
    if not is_success:
        cit.warn("Command Failed")
    return is_success


def read_cmd(cmd: str, verbose: bool = True) -> str:
    """Run command and return command's output

    Args:
        cmd (str): The command.
    Returns:
        str: What the command's output to stdout
    """
    import subprocess

    if verbose:
        cit.echo(cmd, pre="_command")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)  # text=True for str output, shell=True for run cmd directly in shell instead of run cmd.exe
    (proc_stdout, proc_stderr) = proc.communicate(input=None)  # proc_stdin
    if proc.returncode and proc_stderr and verbose:
        cit.warn("Command Failed:")
        cit.print(proc_stderr)
    return proc_stdout  # or proc.returncode


def is_cmd_exist(cmd: str) -> bool:
    """Test if command is available for execution.

    Args:
        cmd (str): The command.

    Returns:
        bool: if the command is exist
    """
    base_cmd = cmd.split()[0].strip()
    if shutil.which(base_cmd) is not None:  # Command is a executable under PATH
        return True
    if platform.system() == "Windows":  # Windows
        result = os.system(f"where {base_cmd} >nul 2>&1")
        return (result == 0)
    else:  # Linux, Unix, macOS
        proc = os.popen(f"command -v '{base_cmd}'")  # only bash functions support
        result = proc.read()
        proc.close()
        return (result != "")


def resolve_value(data):
    """Get the value for the current platform from the given input.

    Args:
        data (Any | dict): The data or a dict for datas for different platforms. The dict key is `platform.system()`, and `*` is for default. E.g. {"Windows": ..., "Darwin": ..., "*": Defaults}

    Returns:
        Any: The value for the current platform.
    """
    if isinstance(data, dict):
        result = data.get(platform.system()) or data.get(platform.system().lower()) or data.get(platform.system().upper()) or data.get(platform.system().capitalize())
        if result is None:  # no value for the current platform
            result = data.get('*')  # use the default value
        return result  # return the value even if it's None
    return data  # return the data if it's not a dict


def install_package(name: str | dict, manager: str | dict = {"Windows": "scoop", "Linux": "apt", "Darwin": "brew", "*": "pip3"}) -> bool:
    """Install package using package manager

    Args:
        package (str|dict): The package name or a dict of package names for different platforms. If this is a dict, the key should be the platform name from `platform.system()` or `*` for default, and the value should be the package name.
        manager (str|dict): The package manager or a dict of package managers for different platforms. If is a dict, the key should be the platform name from `platform.system()` or `*` for default, and the value should be the package manager name. Defaults to `{"Windows": "scoop", "Linux": "apt", "Darwin": "brew", "*": "pip3"}`.

    Returns:
        bool: Does this command run successfully
    """
    # check inputs
    if not name:
        cit.err("No package name provided!")
        return False
    cit.info(f"Platform: {platform.system()}")
    manager_name = resolve_value(manager)
    cit.info(f"Package Manager: {manager_name}")
    package_name = resolve_value(name)
    cit.info(f"Package Name: {package_name}")
    # Install package
    available_managers = {
        "scoop": {  # Scoop (Windows)
            "command": "scoop",
            "commandline": "scoop install {}",
        },
        "choco": {  # Chocolatey (Windows)
            "command": "choco",
            "commandline": "choco install {}",
        },
        "brew": {  # Homebrew (macOS)
            "command": "brew",
            "commandline": "brew install {}",
        },
        "port": {  # MacPorts (macOS)
            "command": "port",
            "commandline": "sudo port install {}",
        },
        "apt": {  # APT (Debian/Ubuntu)
            "command": "apt",
            "commandline": "sudo apt install {}",
        },
        "snap": {  # Snap (Ubuntu)
            "command": "snap",
            "commandline": "sudo snap install {}",
        },
        "pip": {  # pip (Python)
            "command": "pip",
            "commandline": "pip install --user {}",
        },
        "pip3": {  # pip3 (Python3)
            "command": "pip3",
            "commandline": "pip3 install --user {}",
        },
        "pipx": {  # pipx (Python)
            "command": "pipx",
            "commandline": "pipx install {}",
        },
        "npm": {  # npm (Node.js)
            "command": "npm",
            "commandline": "npm install -g {}",
        },
    }
    if manager_name:
        current_manager = available_managers.get(manager_name)
    if not current_manager:
        cit.err(f"Unsupported package manager: {manager_name}!")
        return False
    if not is_cmd_exist(current_manager["command"]):
        cit.err(f"{manager_name} is not installed!")
        return False
    return run_cmd(current_manager["commandline"].format(package_name))


def get_path(filepath: str) -> Path:
    """Get file or parent dir absolute path or basename or extension.

    Args:
        filepath (str): The file path. Normally it's `__file__`.

    Returns:
        Path: The path object can be used like str.
    """
    return Path(filepath)


def select_path(multiple: bool = False, dir: bool = False, *args, **kwargs):
    """Open a file dialog to get file or dir path.

    Args:
        multiple (bool): The file dialog select multiple files, and return list.
        dir (bool): The file dialog select dir not file.
        *: Any additional args will considered as filedialog args.

    Returns:
        str: The path of selected file or dir.
        list: The path list of selected files.
    """
    import tkinter
    import tkinter.filedialog
    tkapp = tkinter.Tk()
    tkapp.withdraw()
    tkapp.update()
    if dir:
        path = tkinter.filedialog.askdirectory(*args, **kwargs)
    elif multiple:
        path = tkinter.filedialog.askopenfilenames(*args, **kwargs)
    else:
        path = tkinter.filedialog.askopenfilename(*args, **kwargs)
    tkapp.destroy()
    return path


def bfs_walk(root: str) -> typing.Generator[pathlib.Path, None, None]:
    """Breadth First Search the `root` folder.

    Args:
        root (str): The root folder to traverse.

    Yeilds:
        pathlib.Path: The traversed path.
    """
    queue = [pathlib.Path(os.path.expanduser(root))]  # ensure `~` is expanded
    while queue:
        path = queue.pop(0)
        yield path
        if path.is_dir():  # path included `~` returns False
            queue = [p for p in path.iterdir()] + queue  # insert into the front of the queue


def get_paths(root: str, filter: typing.Callable | None = None) -> list:
    """List folders and files under `root` folder with filter.

    Args:
        root (str): root folder to list.
        filter (callable): a function to indicate if the folder or file should be returned. Defaults to return every path. `filter(path: str) -> bool`.

    Returns:
        list[str]: a list of paths that are filtered by `filter` or everything traversed.
    """
    paths = []
    for path in bfs_walk(root):
        if (not filter) or filter(path):
            paths.append(str(path))
    return paths


@cit.deprecated_by(get_paths)
def get_files(root: str, filter: typing.Callable | None = None):
    pass


def ls_tree(root: str, show_icon: bool = True, ascii: bool = False, to_visible: typing.Callable | None = lambda path: True, to_highlight: typing.Callable | None = lambda path: False, add_suffix: typing.Callable | None = None):
    """Print folders and files under `root` folder in tree structure.

    Args:
        root (str): root folder to list.
        show_icon (bool): show icon for folders and files. Defaults to True.
        ascii (bool): use ascii characters for tree structure. Defaults to False.
        to_visible (callable): a function to indicate if the folder or file should be visible. Default to show every path. `to_visible(path: str) -> bool`.
        to_highlight (callable): a function to indicate if the folder or file should be highlighted. Defaults to highlight nothing. `to_highlight(path: str) -> bool`.
        add_suffix (callable): a function to append as suffix to the folder or file name. Defaults to None. `add_suffix(path: str) -> str`.
    """

    def is_visible(path: pathlib.Path) -> bool:
        """Check if the path has visible files or folders."""
        if not to_visible:
            return False
        if to_visible(path):
            return True
        if path.is_dir():
            for child_path in path.iterdir():  # only direct folders and files in path
                if is_visible(child_path):
                    return True
        return False

    cit_ascii, cit.__ascii__  = cit.__ascii__, ascii
    for path in bfs_walk(root):
        # construct text
        path_text = path.name
        # add prefix
        level = len(path.relative_to(root).parts)
        icon = " " if not show_icon else ("📁" if path.is_dir() else "📄")
        # add suffix
        suffix = add_suffix(path) if add_suffix else ""
        # style hightlights
        if to_highlight and to_highlight(path):  # highlight the path if needed
            path_text = f"[u]{path_text}[/]"
        # style hiddens
        if path.name.startswith("."):  # dim hidden files and folders
            path_text = f"[dim]{path_text}[/]"
        # style dirs
        path_text = f"{path_text}{os.sep if path.is_dir() else ''}"  # add "/" or "\" to the end of the folder name
        # assemble
        full_text = f"{icon} {path_text} {suffix}"
        # print
        if is_visible(path):  # check if the path is visible, or the path include visible files or folders
            cit.echo(full_text, indent=level, bar="")
    cit.__ascii__ = cit_ascii


def show_in_file_manager(path: str, ask: bool = False):
    """Show file in Explorer/Finder/File Manager."""
    import subprocess
    import platform
    if ask:
        if platform.system() == "Windows":
            file_manager = "Explorer"
        elif platform.system() == "Darwin":
            file_manager = "Finder"
        else:
            file_manager = "file manager"
        cit.ask(f"Show in {file_manager}?")
        if cit.get_choice(('Yes', 'No')) == 'No':
            return False
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:  # Unix-like
        subprocess.Popen(["xdg-open", path])


def diff(a, b, meta: bool = False, force_str: bool = False, context: int = 0) -> list:
    """Compare two strings, lists or files and return their differences as list.

    Args:
        a (str|list|file): The source of comparison.
        b (str|list|file): The target of comparison.
        meta (bool): Show the meta data in the first 3 lines.
        force_str (bool): Set to `True` if you wanna force to compare `a` and `b` as string. Default is False.
        context (int): Number of context lines returns with diffs. Default is 0, no context lines shows.

    Returns:
        list: Diffs where the dst is not same as src. Only lines with diffs in the result. The first 2 lines are the header of diffs.
    """
    import difflib

    src, dst = {'raw': a}, {'raw': b}
    for d in (src, dst):
        if isinstance(d['raw'], str):
            as_path = get_path(d['raw'])
            if (not force_str) and as_path.exists:
                d['label'] = as_path.basename  # filename will show in header of diffs
                with open(as_path, encoding='utf-8') as f:
                    d['content'] = f.readlines()
            else:
                d['label'] = str(str)
                d['content'] = d['raw'].split('\n')  # convert str to list for comparison. Ex. ['str',]
        else:
            d['label'] = str(type(d['raw']))
            d['content'] = d['raw']
    diffs = difflib.unified_diff(src['content'], dst['content'], n=context, fromfile=src['label'], tofile=dst['label'])
    diffs = [ln.strip('\n') for ln in diffs]  # Ensure no \n returns
    return diffs if meta else diffs[3:]


def update_file(filename: str, url: str) -> bool:
    """Check and update file compares with remote_url

    Args:
        filename (str): Local filename, normally it's `__file__`
        url (str|urllib.request.Request): Remote url of raw file content. Use urllib.request.Request object for headers.
    Returns:
        bool: File updated or not
    """
    def compare(s1, s2):
        return s1 == s2, len(s2) - len(s1)

    if not url or not filename:
        return False
    try:
        raw_codes = read_url(url)
        if not raw_codes:
            cit.err("Failed to get remote file content.")
            return False
        with open(filename, "rb") as f:
            current_codes = f.read().replace(b"\r", b"")
        is_same, diff = compare(current_codes, raw_codes)
        if is_same:
            cit.info("{} is already up-to-date.".format(filename))
            return False
        else:
            cit.ask("A new version is available. Update? (Diff: {})".format(diff))
            if cit.get_choice(["Yes", "No"]) == "Yes":
                with open(filename, "wb") as f:
                    f.write(raw_codes)
                cit.info("Update Success.")
                return True
            else:
                cit.warn("Update Canceled")
                return False
    except Exception as e:
        cit.err("{f} update failed: {e}".format(f=filename, e=e))
        return False


def read_file(filepath, *args, **kwargs) -> str:
    """Try different encoding to open a file in readonly mode."""
    for mode in ("utf-8", "gbk", "cp1252", "windows-1252", "latin-1", "ascii"):
        try:
            with open(filepath, *args, encoding=mode, **kwargs) as f:
                content = f.read()
                cit.info("File is read in {} mode.".format(mode))
                return content
        except UnicodeDecodeError:
            cit.warn("File cannot be opened in {} mode".format(mode))
    with open(filepath, *args, encoding='ascii', errors='surrogateescape', **kwargs) as f:
        content = f.read()
        cit.info("File is read in ASCII surrogate escape mode.")
        return content


def read_url(source) -> bytes:
    """Try to get file content from the url

    Args:
        source (str|Request): The target url.

    Returns:
        bytes: The content of the request's response.
    """
    response = urllib.request.urlopen(source)
    return response.read() if response else b""


def copy_file(*args, **kwargs) -> str:
    """Copy file from one place to another.

    Args:
        *args, **kwargs: All the arguments and keyword arguments will be passed to `move_file` function, except `copy` is set to `True`. Copying when moving is logical, moving when copying is not.

    Returns:
        Returns whatever `move_file` returns.
    """
    kwargs['copy'] = True  # Override the `copy` argument to `True`
    return move_file(*args, **kwargs)


def move_file(src: str, dst: str, copy: bool = False, backup: bool = False, ensure: bool = False, msgout: typing.Callable | None = None) -> str:
    """Move or copy file from one place to another.

    Args:
        src (str): Source file path.
        dst (str): Destination file path.
        copy (bool): Copy or move source file to destination.
        backup (bool): Backup destination file or not. `True` means try to backup destination file, pass if destination file does not exist.
        ensure (bool): Ensure the destination parent directory exists or not. `True` means create the parent directory if not exists, and ignore if the parent directory exists.
        msgout (callable): Output function to handle the outputs. `None` means no outputs.

    Returns:
        str: The destination file path.
    """
    import time

    def _msg(message):
        if msgout:
            msgout(message)
    _msg(f"Source File: {src}")
    src = get_path(src)
    _msg(f"Destination File: {dst}")
    dst = get_path(dst)
    if copy:
        _msg("Copy Enabled.")
    if backup:
        _msg("Backup Enabled.")
    if ensure:
        _msg("Ensure Enabled.")
    if not src.exists:
        raise FileNotFoundError("Source file does not exist.")
    if ensure:
        if not dst.parent.exists:
            os.makedirs(dst.parent, exist_ok=True)
            _msg(f"Destination file parent directory created: {dst.parent}")
    if dst.exists:
        if backup:
            dst_backup = f"{ dst}.backup.{time.strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(dst, dst_backup)
            _msg(f"Destination file backuped up to `{dst_backup}`.")
        else:
            _msg("Warning: Destination file already exists and will be overwritten.")
    else:
        if backup:
            _msg("Warning: Destination file does not exist, backup skipped.")
    if copy:
        _msg(f"File {src} copied to {dst}.")
        return shutil.copy2(src, dst)
    else:
        _msg(f"File {src} moved to {dst}.")
        return shutil.move(src, dst)


def ajax(url: str, param: dict = {}, method: str = "get"):
    """Get response using AJAX.

    Args:
        url (str): The requesting url.
        param (dict): The parameters in the request payload.
        method (str): The method of request, "get" or "post".
    Returns:
        dict: The responsed json decoded into a dict.
    """
    if method.lower() == "get":
        if param:
            param_enc = urllib.parse.urlencode(param)
            url += "?" + param_enc
        req = urllib.request.Request(url)
    elif method.lower() == "post":
        param_enc = json.dumps(param).encode("utf-8")
        req = urllib.request.Request(url, data=param_enc)
    else:
        raise Exception("invalid method '{}' (GET/POST)".format(method))
    rsp_bytes = read_url(req)
    if rsp_bytes:
        rsp_str = rsp_bytes.decode("utf-8")
        try:
            return json.loads(rsp_str)
        except json.decoder.JSONDecodeError:
            return rsp_str
    return None


def is_python3() -> bool:
    """Check does the script is running in python3"""
    return sys.version_info[0] == 3


def is_admin() -> bool | None:
    """Check does the script has admin privileges."""
    import ctypes
    if platform.system() == "Windows":  # Windows only
        return ctypes.windll.shell32.IsUserAnAdmin()
    return None


def runas_admin(py_file: str) -> bool:
    """Execute a python script with admin privileges.

    Links:
        Syntax of ShellExecuteW: https://docs.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew

    Args:
        py_file (str): The command line arguments passed to python. It should be the script path, such as `__file__`.

    Returns:
        bool: Command run success.
    """
    import ctypes
    if not platform.system() == 'Windows':
        return False
    parent_window_handle = None  # no UI
    operation = "runas"  # run as admin
    executor = sys.executable  # python.exe
    parameter = py_file
    directory = None  # using current working directory.
    SHOWNORMAL = 1  # SW_SHOWNORMAL
    if not os.path.isfile(parameter):
        raise FileNotFoundError(parameter)
    return_code = ctypes.windll.shell32.ShellExecuteW(parent_window_handle, operation, executor, parameter, directory, SHOWNORMAL)
    return return_code > 32  # should be greater than 32 if execute success
