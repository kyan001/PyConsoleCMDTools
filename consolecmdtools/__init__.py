# -*- coding: utf-8 -*-
import os
import sys
import urllib.request
import json
import io
import pathlib
# !! some imports are lazy-loaded

import consoleiotools as cit

from .path import Path


__version__ = '6.0.1'


def banner(text: str) -> str:
    """Generate a banner of 3 lines"""
    FILLER = "#"
    text = text.strip()
    middle_line = FILLER + text.center(int(len(text) / 0.618)) + FILLER
    top_line = bottom_line = FILLER * len(middle_line)
    return "\n".join([top_line, middle_line, bottom_line])


def md5(target, force_text=False) -> str:
    """Generate MD5 hash for bytes, str, int, file, etc."""
    import hashlib

    if not target:
        return None
    if not force_text and os.path.isfile(target):  # if target is a file
        with open(target, 'rb') as f:
            content = f.read().replace(os.linesep.encode(), b"\n")  # universal newline
            return hashlib.md5(content).hexdigest()
    if type(target) != bytes:  # the input of hashlib.md5() should be type of bytes
        target = str(target).encode()
    return hashlib.md5(target).hexdigest()


def crc32(target, force_text=False) -> int:
    """Generate CRC32 hash for bytes, str, int, file, etc."""
    import binascii

    if not target:
        return 0
    if not force_text and os.path.isfile(target):  # if target is a file
        with open(target, 'rb') as f:
            content = f.read().replace(os.linesep.encode(), b"\n")  # universal newline
            return binascii.crc32(content)
    if type(target) != bytes:  # if target is str/int/float, the input of binascii.crc32() should be type of bytes
        target = str(target).encode()
    return binascii.crc32(target)


def main_color(source: str, scale: int = 200, triplet: str = "rgb", is_url: bool = False) -> str:
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
    statistics = {
        "r": 0,
        "g": 0,
        "b": 0,
        "coef": 0
    }
    for count, (r, g, b, a) in img.getcolors(img.size[0] * img.size[1]):  # get each color used in image with its count, maxcolors = the size of the image.
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        saturation = s * 255  # extend the range from 0~1 to 0~255
        coefficient = (saturation * count * a) or 0.01  # get how important this color is. Should not be 0.
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
    if sys.platform.startswith("win"):  # Windows
        os.system("cls")
    elif os.name == "posix":  # Linux and Unix
        os.system("clear")
    elif sys.platform == "darwin":  # macOS
        os.system("clear")
    else:
        cit.err("No clearScreen for " + sys.platform)


def get_py_cmd() -> str:
    """Get OS's python command"""
    if sys.platform.startswith("win"):
        return "py"
    elif os.name == "posix":
        return "python3"
    elif sys.platform == "darwin":
        return "python3"
    else:
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


def read_cmd(cmd: str) -> str:
    """Run command and return command's output

    Args:
        cmd (str): The command.
    Returns:
        str: What the command's output to stdout
    """
    import shlex
    import subprocess

    cit.echo(cmd, pre="command")
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (proc_stdout, proc_stderr) = proc.communicate(input=None)  # proc_stdin
    return proc_stdout.decode()  # Decode stdout and stderr bytes to str


def is_cmd_exist(cmd: str) -> bool:
    """Test if command is available for execution

    Args:
        cmd (str): The command.
    Returns:
        bool: if the command is exist
    """
    if sys.platform.startswith('win'):  # Windows
        result = os.system("where {} >nul 2>&1".format(cmd))
        return (result == 0)
    else:  # Linux, Unix, macOS
        proc = os.popen("command -v {}".format(cmd))
        result = proc.read()
        proc.close()
        return (result != "")


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


def bfs_walk(root: str) -> pathlib.Path:
    """Breadth First Search the `root` folder."""
    queue = [pathlib.Path(root)]
    while queue:
        path = queue.pop(0)
        yield path
        if path.is_dir():
            queue = [p for p in path.iterdir()] + queue  # insert into the front of the queue


def get_files(root: str, filter: callable = None) -> list[str]:
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


def ls_tree(root: str, show_icon: bool = True, ascii: bool = False, to_visible: callable = lambda path: True, to_highlight: callable = lambda path: False, add_suffix: callable = None):
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

    for path in bfs_walk(root):
        # construct text
        path_text = path.name
        # add prefix
        depth = len(path.relative_to(root).parts)
        icon = " " if not show_icon else ("📁" if path.is_dir() else "📄")
        indent_char = f"[dim]{'|' if ascii else '│'}[/]   "
        dash_char = f"{'|--' if ascii else '├──'}{icon}"
        prefix = (indent_char * (depth - 1) + dash_char) if depth > 0 else "📂"  # add tree branchs characters
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
        full_text = f"{prefix} {path_text} {suffix}"
        # print
        if is_visible(path):  # check if the path is visible, or the path include visible files or folders
            cit.print(full_text)


def show_in_file_manager(path: str, ask: bool = False):
    """Show file in Explorer/Finder/File Manager."""
    import subprocess
    import platform
    if ask:
        if sys.platform.startswith("win"):
            file_manager = "Explorer"
        elif platform.system() == "Darwin":
            file_manager = "Finder"
        else:
            file_manager = "file manager"
        cit.ask(f"Show in {file_manager}?")
        if cit.get_choice(('Yes', 'No')) == 'No':
            return False
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
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
            if (not force_str) and os.path.isfile(d['raw']):
                d['label'] = os.path.basename(d['raw'])  # filename will show in header of diffs
                with open(d['raw'], encoding='utf-8') as f:
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
    return response.read() if response else None


def move_file(src: str, dst: str, copy: bool = False, backup: bool = False, msgout: callable = None):
    """Move or copy file from one place to another.

    Args:
        src (str): Source file path.
        dst (str): Destination file path.
        copy (bool): Copy or move source file to destination.
        backup (bool): Backup destination file or not. `True` means try to backup destination file, pass if destination file does not exist.
        msgout (callable): Output function to handle the outputs. `None` means no outputs.
    """
    import time
    import shutil

    def _msg(message):
        if msgout:
            msgout(message)
    _msg(f"Source File: {src}")
    _msg(f"Destination File: {dst}")
    if copy:
        _msg("Copy Enabled.")
    if backup:
        _msg("Backup Enabled.")
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source file does not exist.")
    if os.path.exists(dst):
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
        shutil.copy2(src, dst)
    else:
        shutil.move(src, dst)
    _msg(f"File {src} {'copied' if copy else 'moved'} to {dst}.")


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
            param = urllib.parse.urlencode(param)
            url += "?" + param
        req = urllib.request.Request(url)
    elif method.lower() == "post":
        param = json.dumps(param).encode("utf-8")
        req = urllib.request.Request(url, data=param)
    else:
        raise Exception("invalid method '{}' (GET/POST)".format(method))
    rsp_bytes = read_url(req)
    if rsp_bytes:
        rsp_str = rsp_bytes.decode("utf-8")
        try:
            return json.loads(rsp_str)
        except json.decoder.JSONDecodeError as e:
            return rsp_str
    return None


def is_python3() -> bool:
    """Check does the script is running in python3"""
    return sys.version_info[0] == 3


def is_admin() -> bool:
    """Check does the script has admin privileges."""
    import ctypes
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:  # Windows only
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
