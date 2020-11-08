# -*- coding: utf-8 -*-
import os
import sys
import urllib.request
import json
import io
# !! some imports are lazy-loaded

import consoleiotools as cit

__version__ = '1.0.1'


def banner(text: str) -> str:
    """Generate a banner of 3 lines"""
    FILLER = "#"
    text = text.strip()
    middle_line = FILLER + text.center(int(len(text) / 0.618)) + FILLER
    top_line = bottom_line = FILLER * len(middle_line)
    return "\n".join([top_line, middle_line, bottom_line])


def md5(text) -> str:
    """Generate md5 hash for bytes, string, int, etc."""
    import hashlib

    if not text:
        return None
    if type(text) != bytes:  # the input of hashlib.md5() should be type of bytes
        text = str(text).encode()
    return hashlib.md5(text).hexdigest()


def image_to_color(url: str, scale: int = 200, mode: str = "rgb") -> tuple:
    """Get a representative color from the url-pointed image"""
    from PIL import Image
    import colorsys

    if not url:
        return None
    response = urllib.request.urlopen(url)
    img_buffer = io.BytesIO(response.read())
    img = Image.open(img_buffer).convert("RGBA")
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
    if mode.lower() == "hex":
        return "#%0.2X%0.2X%0.2X" % color
    else:
        return color


def clear_screen():
    """Clear the console screen"""
    if sys.platform.startswith('win'):  # Windows
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
        cit.err("No python3 command for " + sys.platform)


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


def get_dir(filename: str) -> tuple:
    """Get file dir's name and dir's basename.

    If file located at /path/to/dir/file, then the dirname is "/path/to/dir", and basename is "dir"

    Args:
        filename: str. Local filename, normally it's __file__

    Returns:
        tuple(
            str: File dir's path
            str: File dir's basename
        )
    """
    dir_path = os.path.dirname(os.path.abspath(filename))
    dir_basename = os.path.basename(dir_path)
    return dir_path, dir_basename


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
        url: str. Remote url of raw file content, normally it's https://raw.githubcontents.com/...
    Returns:
        bool: file updated or not
    """
    def compare(s1, s2):
        return s1 == s2, len(s2) - len(s1)

    if not url or not filename:
        return False
    try:
        req = urllib.request.urlopen(url)
        raw_codes = req.read()
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


def read_file(filepath: str) -> str:
    """Try different encoding to open a file in readonly mode."""
    for mode in ("utf-8", "gbk", "cp1252", "windows-1252", "latin-1"):
        try:
            with open(filepath, mode="r", encoding=mode) as f:
                content = f.read()
                cit.info("以 {} 格式打开文件".format(mode))
                return content
        except UnicodeDecodeError:
            cit.warn("打开文件：尝试 {} 格式失败".format(mode))
    return None


def ajax(url: str, param: dict = {}, method: str = "get"):
    """Get response using AJAX.

    Args:
        url: string. The requesting url.
        param: dict. The parameters in the request payload.
        method: str. The method of request, "get" or "post".
    Returns:
        dict: The responsed json decoded into a dict.
    """
    param = urllib.parse.urlencode(param)
    if method.lower() == "get":
        req = urllib.request.Request(url + "?" + param)
    elif method.lower() == "post":
        param = param.encode("utf-8")
        req = urllib.request.Request(url, data=param)
    else:
        raise Exception("invalid method '{}' (GET/POST)".format(method))
    rsp = urllib.request.urlopen(req)
    if rsp:
        rsp_json = rsp.read().decode("utf-8")
        rsp_dict = json.loads(rsp_json)
        return rsp_dict
    return None
