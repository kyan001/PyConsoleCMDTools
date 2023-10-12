# PyConsoleCMDTools
![PyPI - Downloads](https://img.shields.io/pypi/dm/consolecmdtools)
![GitHub release](https://img.shields.io/github/v/release/kyan001/PyConsoleCMDTools)
[![GitHub license](https://img.shields.io/github/license/kyan001/PyConsoleCMDTools.svg)](https://github.com/kyan001/PyConsoleCMDTools/blob/master/LICENSE)

## Installation

```sh
pip install consolecmdtools  # install
pip install --upgrade consolecmdtools  # update
python -m consolecmdtools  # examples
```

## Get Started

```python
import consolecmdtools as cct
print(cct.__version__)
```

## Functions

```python
>>> cct.banner("hello, world!")  # Generate banner for text
#######################
#    hello, world!    #
#######################

>>> cct.md5("blah blah blah")  # Return md5 hash for text.
'55e562bfee2bde4f9e71b8885eb5e303'

>>> cct.md5(42)  # Return md5 hash for number.
'a1d0c6e83f027327d8461063f4ac58a6'

>>> cct.md5('file.txt')  # Return md5 hash for file.
'd07aa6ddab4d6d2d2891aa9f3625a5db'

>>> cct.md5('file.txt', force_text=True)  # Force to return the md5 has for text, even the file exists.
'3d8e577bddb17db339eae0b3d9bcf180'

>>> cct.crc32("blah blah blah")  # Return crc32 hash for text.
753353432

>>> cct.crc32(42)  # Return crc32 hash for number.
841265288

>>> cct.crc32('file.txt')  # Return crc32 hash for file.
1030388931

>>> cct.crc32('file.txt', force_text=True)  # Force to return the md5 has for text, even the file exists.
3774289445

>>> cct.main_color('image.jpg')  # Get theme color of image.
(152, 156, 69)  # RGB value

>>> cct.main_color('http://image-url/image', is_url=True)  # Get theme color of web image.
(152, 156, 69)  # RGB value

>>> cct.main_color('image.jpg', scale=500)  # Cost more time to generate a preciser color. default scale is 200.
(152, 156, 69)

>>> cct.main_color('image.jpg', triplet='hex')  # Return color in hex triplet format. default mode is 'rgb'.
'#989C45'

>>> cct.clear_screen()  # Clear the console.

>>> cct.get_py_cmd()  # Get python running command for different OS.
'python3'

>>> cct.run_cmd("echo hello")  # Run console command. If the command failed, a warning message echoed. Returns bool.
*
| __RUN COMMAND__________________________
| (Command) echo hello
hello
`

>>> cct.read_cmd("echo hello")  # Run a command and return the output.
'hello\n'

>>> cct.is_cmd_exist("ls")  # Test if a command is exist.
True

>>> cct.get_path("./file.txt")  # Get the absolute path.
Path('/path/to/file.txt')  # Path Object which is a subclass of str.

>>> cct.get_path("./file.txt").split('/')  # Path Object can be used as str.
['path', 'to', 'file.txt']

>>> cct.get_path("./file.txt").path  # Get the original path.
'./file.txt'

>>> cct.get_path("./file.txt").abs  # Get the absolute path. Same as `get_path("./file.txt")` itself.

>>> cct.get_path("/path/to/file.txt").basename  # Get the basename of the file or dir.
'file.txt'

>>> cct.get_path("/path/to/file.txt").ext  # Get the extension of the path. If the path is a dir, return ''.
'txt'

>>> cct.get_path("/path/to/file.txt").stem  # Get the name of the path without extension. If the path is a dir, return its basename.
'file'

>>> cct.get_path("/path/to/file.txt").parent  # Get the parent dir path of the file or dir.
'/path/to'

>>> cct.get_path("/path/to/file.txt").parent.basename  # Get the parent dir path's basename of the file or dir.
'to'

>>> cct.select_path()  # Show file dialog to get file path. Additional args pass to tkinter.filedialog.askopenfilename()
'/path/to/file'

>>> cct.select_path(multiple=True)  # Show file dialog to get multiple file paths.
['/path/to/file1', '/path/to/file2']

>>> cct.select_path(dir=True)  # Show file dialog to get dir path.
'/path/to/dir'

>>> cct.bfs_walk("/path/to/root")  # Get all paths in the root dir using Breadth-first search.
['/path/to/root', '/path/to/root/folder', '/path/to/root/folder/file1', '/path/to/root/folder/file2']

>>> cct.get_files("/path/to/root", filter=lambda path: path.name.startswith("f"))  # Filter paths and return as list[str]
['/path/to/root/folder', '/path/to/root/folder/file1', '/path/to/root/folder/file2']

>>> cct.ls_tree(root="/path/to/root")  # Show folders and files in a tree.
📂 root\
├──📁 folder\
│   ├──📄 file1
│   ├──📄 file2

>>> cct.ls_tree(root="/path/to/root", show_icon=False, ascii=True)  # Show without icons, using ASCII chars.
root/
|-- folder/
|  |-- file1
|  |-- file2

>>> cct.ls_tree(root="/path/to/root", to_visible=lambda path: path.is_dir())  # Show only folders.
📂 root\
├──📁 folder\

>>> cct.ls_tree(root="/path/to/root", to_highlight=lambda path: path.name == "file1")  # Highlight certain file.
📂 root\
├──📁 folder\
│   ├──📄 file1  # highlighted
│   ├──📄 file2

>>> cct.ls_tree(root="/path/to/root", add_suffix=lambda path: "(current)" if pathe.name == "file1" else "")  # Add suffix to path name.
📂 root\
├──📁 folder\
│   ├──📄 file1 (current)
│   ├──📄 file2

>>> cct.show_in_file_manager("/path/to/file")  # Show file in Explorer/Finder/File Manager.

>>> cct.show_in_file_manager("/path/to/file", ask=True)  # Ask before show.

>>> cct.diff("str1", "str2")  # Compare 2 strings, return the list of diffs.
[  # you can use `"\n".join(diff)` to print the diff.
    "-str1",
    "+str2"
]

>>> cct.diff("str1", "str2", meta=True)  # show meta data in the first 3 lines.
[
    "--- <class 'str'>",
    "+++ <class 'str'>",
    "@@ -1 +1 @@",
    "-str1",
    "+str2"
]


>>> cct.diff(["a", "b"], ["a", "b", "c"])  # Compare 2 lists and print diffs.
[
    "+c"
]

>>> cct.diff(["a", "b"], ["a", "b", "c"], context=2)  # Show diffs with 2 extra context lines.
[
    " a",  # context line
    " b",  # context line
    "+c"  # diff
]

>>> cct.diff("/path/to/file1", "/path/to/file2")  # Compare between 2 files.

>>> cct.diff("/path/to/file1", "str")  # Compare between file and str/list.

>>> cct.diff('str', 'str')  # If no diff, return [].
[]

>>> cct.update_file('file', 'http://file-url')  # Update file if the file is not as same as url content.
False  # if already up-to-date.

>>> cct.read_file('file')  # Read file using different encoding automatically.
"file content"

>>> cct.move_file("/path/to/src", "/path/to/dst")  # Move file from src to dst, overwrite if dst already exists.

>>> cct.move_file("/path/to/src", "/path/to/dst", copy=True)  # Copy file from src to dst.

>>> cct.move_file("/path/to/src", "/path/to/dst", backup=True)  # Backup dst file before move or copy.

>>> cct.move_file("/path/to/src", "/path/to/dst", msgout=print)  # Use `print` to handle output logs.

>>> cct.ajax('http://ajax-url')  # Start a AJAX request.
{'result': 'data'}  # As python dict.

>>> cct.ajax('http://ajax-url', {'data': 'value'})  # AJAX request with param.
{'result': 'data'}

>>> cct.ajax('http://ajax-url', method='post')  # AJAX request using post. default is 'get'.
{'result': 'data'}

>>> if not cct.is_admin():  # Check does the script has admin privileges.
...     cct.runas_admin(__file__)  # run the script with admin privileges.
... else:
...     # your code here
```

## Updates
* 2021-01-29 v3.0.0:
    * Deprecated `image_to_color()`, add `main_color()`.
        * use `main_color(..., is_url=True)` instead of `image_to_color(...)`
