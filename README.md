# PyConsoleCMDTools
[![Build Status](https://travis-ci.org/kyan001/PyConsoleCMDTools.svg?branch=master)](https://travis-ci.org/kyan001/PyConsoleCMDTools)
![PyPI - Downloads](https://img.shields.io/pypi/dm/consolecmdtools.svg)
![GitHub release](https://img.shields.io/github/release/kyan001/PyConsoleCMDTools.svg)
[![GitHub license](https://img.shields.io/github/license/kyan001/PyConsoleCMDTools.svg)](https://github.com/kyan001/PyConsoleCMDTools/blob/master/LICENSE)

A console toolkit for common uses


## Installation

```sh
pip install consolecmdtools  # install
pip install --upgrade consolecmdtools  # update
```

## Get Started

```python
>>> import consolecmdtools as cct
>>> print(cct.__version__)
'1.0.1'
```

## Functions

```python
>>> print(cct.banner("hello, world!"))  # Generate banner for text
#######################
#    hello, world!    #
#######################

>>> cct.md5("KyanToolKit")  # Return md5 hash for text.
'a7599cb70a39f9d9d18a76608bf21d4e'

>>> cct.image_to_color('http://image-url/image')  # Get theme color of image.
(152, 156, 69)  # RGB value

>>> cct.image_to_color('http://image-url/image', scale=500)  # Cost more time to generate a preciser color. default scale is 200.
(152, 156, 69)

>>> cct.image_to_color('http://image-url/image', mode='hex')  # Return color in hex. default mode is 'rgb'.
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

>>> cct.get_dir("./file")  # Get the path and basename of the parent folder of the file.
("/path/to/dir", "dir")  # '/path/to/dir/file' for example

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

>>> cct.ajax('http://ajax-url')  # Start a AJAX request.
{'result': 'data'}  # As python dict.

>>> cct.ajax('http://ajax-url', {'data': 'value'})  # AJAX request with param.
{'result': 'data'}

>>> cct.ajax('http://ajax-url', method='post')  # AJAX request using post. default is 'get'.
{'result': 'data'}
```
