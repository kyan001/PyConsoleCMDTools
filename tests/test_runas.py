import os
import ctypes
import tempfile

with tempfile.TemporaryDirectory() as tmpd:
    tmp_file = os.path.join(tmpd, "admin_test_result.txt")
    with open(tmp_file, 'w') as f:
        f.write(str(ctypes.windll.shell32.IsUserAnAdmin()))
    with open(tmp_file) as f:
        if f.read() == "2":
            exit(0)  # ok
        else:
            exit(1)  # ko
