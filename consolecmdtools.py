# -*- coding: utf-8 -*-
import os
import sys
import urllib.request
import json
import io
# !! some imports are lazy-loaded

import consoleiotools as cit

__version__ = '3.2.5'


def banner(text: str) -> str:
    """Generate a banner of 3 lines"""
    FILLER = "#"
    text = text.strip()
    middle_line = FILLER + text.center(int(len(text) / 0.618)) + FILLER
    top_line = bottom_line = FILLER * len(middle_line)
    return "\n".join([top_line, middle_line, bottom_line])


def md5(target, force_text=False) -> str:
    """Generate MD5 hash for bytes, string, int, file, etc."""
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
    """Generate CRC32 hash for bytes, string, int, file, etc."""
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


def main_color(source: str, scale: int = 200, triplet: str = "rgb", is_url: bool = False) -> tuple:
    """Get a representative color from the source-pointed image

    Imports:
        colorsys: shipped with python.
        PIL: use `pip install pillow` or install by package manager (apt, apk, etc).

    Args:
        source: str. The URL of the image, or the filepath.
        scale: int. The size of generated image thumbnail.
        triplet: str. The return value format. `rgb` for RGB triplet: (255, 255, 255), and `hex` for HEX triplet: '#FFFFFF'.
        is_url: The source should be downloaded or not.

    Returns:
        The main color of the source image in RGB or HEX format.
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
        cmd: string
    Returns:
        bool: Does this command run successfully
    """
    SUCCESS_CODE = 0
    cit.echo(cmd, "command")
    is_success = (os.system(cmd) == SUCCESS_CODE)
    if not is_success:
        cit.warn("Command Failed")


def read_cmd(cmd: str) -> str:
    """Run command and return command's output

    Args:
        cmd: string
    Returns:
        str: What the command's output to stdout
    """
    import shlex
    import subprocess

    cit.echo(cmd, "command")
    args = shlex.split(cmd)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    (proc_stdout, proc_stderr) = proc.communicate(input=None)  # proc_stdin
    return proc_stdout.decode()  # Decode stdout and stderr bytes to str


def is_cmd_exist(cmd: str) -> bool:
    """Test if command is available for execution

    Args:
        cmd: string
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


def get_dir(filename: str, mode: str = 'dir') -> str:
    """Get file dir's name and dir's basename.

    If file located at /path/to/dir/file, then the dirname is "/path/to/dir", and basename is "dir"

    Args:
        filename: str. Local filename, normally it's __file__.
        mode: str. `file` return the file path, `dir` return the dir path, `basename` return dir basename.

    Returns:
        str: file path or dir path or dir basename based on mode.
    """
    file_path = os.path.abspath(filename)
    dir_path = os.path.dirname(file_path)
    dir_basename = os.path.basename(dir_path)
    if mode == 'file':
        return os.path.abspath(filename)
    elif mode == 'dir':
        return dir_path
    elif mode == 'basename':
        return dir_basename
    else:
        return dir_path


def select_path(multiple: bool = False, folder: bool = False, *args, **kwargs):
    """Open a file dialog to get file or folder path.

    Args:
        multiple: bool. The file dialog select multiple files, and return list.
        folder: bool. The file dialog select folder not file.
        *: Any additional args will considered as filedialog args.

    Returns:
        str: The path of selected file or folder.
        list: The path list of selected files.
    """
    import tkinter
    import tkinter.filedialog
    tkapp = tkinter.Tk()
    tkapp.withdraw()
    tkapp.update()
    if folder:
        path = tkinter.filedialog.askdirectory(*args, **kwargs)
    elif multiple:
        path = tkinter.filedialog.askopenfilenames(*args, **kwargs)
    else:
        path = tkinter.filedialog.askopenfilename(*args, **kwargs)
    tkapp.destroy()
    return path


def diff(a, b, meta: bool = False, force_str: bool = False, context: int = 0) -> list:
    """Compare two strings, lists or files and return their differences as list.

    Args:
        a: str/list/file. The source of comparison.
        b: str/list/file. The target of comparison.
        meta: bool. Show the meta data in the first 3 lines.
        force_str: bool. Set to `True` if you wanna force to compare `a` and `b` as string. Default is False.
        context: int. Number of context lines returns with diffs. Default is 0, no context lines shows.

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
        filename: str. Local filename, normally it's `__file__`
        url: str or urllib.request.Request object. Remote url of raw file content. Use urllib.request.Request object for headers.
    Returns:
        bool: file updated or not
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
        source: str or Request. The target url.

    Returns:
        bytes: The content of the request's response.
    """
    response = urllib.request.urlopen(source)
    return response.read() if response else None


def ajax(url: str, param: dict = {}, method: str = "get"):
    """Get response using AJAX.

    Args:
        url: string. The requesting url.
        param: dict. The parameters in the request payload.
        method: str. The method of request, "get" or "post".
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
        py_file: string. The command line arguments passed to python. It should be the script path, such as `__file__`.
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
