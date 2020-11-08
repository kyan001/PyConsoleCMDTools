#!/usr/bin/env python3
import sys
import os
import unittest
import getpass
from unittest.mock import patch

import FakeOut
import FakeIn
import FakeOs

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)
import consolecmdtools as cct  # noqa


class test_consolecmdtools(unittest.TestCase):
    """consolecmdtools unit tests"""
    cct_version = '1.0.0'

    def setUp(self):
        # redirect stdout
        self.console_out = sys.stdout
        self.fakeout = FakeOut.FakeOut()
        sys.stdout = self.fakeout
        # redirect stdin
        self.console_in = sys.stdin
        self.fakein = FakeIn.FakeIn()
        sys.stdin = self.fakein
        # monkey patch
        self.os_system = os.system
        self.fakeos = FakeOs.FakeOs()
        os.system = self.fakeos.system

    def tearDown(self):
        # clean fakin/out buffer
        self.fakeout.clean()
        self.fakein.clean()
        self.fakeos.clean()
        # set back stdin/out to console
        sys.stdout = self.console_out
        sys.stdin = self.console_in
        os.system = self.os_system

    def test_version(self):
        self.assertEqual(self.cct_version, cct.__version__)

    def test_banner(self):
        expect_word = '################\n#  Test Text   #\n################'
        self.assertEqual(expect_word, cct.banner("Test Text"))

    def test_md5_string(self):
        md5 = cct.md5("Test Text")
        self.assertEqual(md5, 'f1feeaa3d698685b6a6179520449e206')

    def test_md5_int(self):
        md5 = cct.md5(123)
        self.assertEqual(md5, '202cb962ac59075b964b07152d234b70')

    def test_md5_bytes(self):
        md5 = cct.md5(b'Test Text')
        self.assertEqual(md5, 'f1feeaa3d698685b6a6179520449e206')

    def test_image_to_color_rgb(self):
        img_url = "https://github.com/kyan001/PyConsoleCMDTools/raw/main/tests/image.jpg"
        color = cct.image_to_color(img_url)
        self.assertEqual(color, (227, 174, 106))

    def test_image_to_color_hex(self):
        img_url = "https://github.com/kyan001/PyConsoleCMDTools/raw/main/tests/image.jpg"
        color = cct.image_to_color(img_url, mode='hex')
        self.assertEqual(color, '#E3AE6A')

    def test_clear_screen(self):
        cct.clear_screen()
        self.assertTrue(self.fakeos.readline() in 'cls clear')

    def test_get_py_cmd(self):
        result = cct.get_py_cmd()
        self.assertTrue(result in ('py', 'python3'))

    def test_run_cmd(self):
        cct.run_cmd("Test Command")
        self.assertEqual(self.fakeos.readline(), "Test Command")

    def test_read_cmd(self):
        self.assertEqual(cct.read_cmd("echo Test Text"), "Test Text\n")

    def test_is_cmd_exist(self):
        with patch("os.system", new=self.os_system):
            self.assertFalse(cct.is_cmd_exist("notexist"))
            self.assertTrue(cct.is_cmd_exist("ls"))

    def test_get_dir(self):
        dir_path, dir_basename = cct.get_dir(__file__)
        self.assertTrue(dir_path.endswith("tests"))
        self.assertEqual(dir_basename, "tests")

    def test_diff_same(self):
        diffs = cct.diff("test", "test")
        self.assertFalse(diffs)

    def test_diff_str(self):
        a, b = "test1", "test2"
        expect_diff = [
            "-test1",
            "+test2"
        ]
        self.assertEqual(cct.diff(a, b), expect_diff)

    def test_diff_meta(self):
        a, b = "test1", "test2"
        expect_diff = [
            "--- <class 'str'>",
            "+++ <class 'str'>",
            "@@ -1 +1 @@",
            "-test1",
            "+test2"
        ]
        self.assertEqual(cct.diff(a, b, meta=True), expect_diff)

    def test_diff_list(self):
        a, b = ["a", "c"], ["b", "c"]
        expect_diff = [
            "-a",
            "+b"
        ]
        self.assertEqual(cct.diff(a, b), expect_diff)

    def test_diff_context(self):
        a, b = ["a", "c"], ["b", "c"]
        expect_diff = [
            "-a",
            "+b",
            " c"
        ]
        self.assertEqual(cct.diff(a, b, context=1), expect_diff)

    def test_diff_file(self):
        a = os.path.join(project_dir, "tests", "testfile")
        b = "This file should not changed too"
        expect_diff = [
            "-This file should not changed",
            "+This file should not changed too"
        ]
        self.assertEqual(cct.diff(a, b), expect_diff)

    def test_diff_files(self):
        a = os.path.join(project_dir, "tests", "testfile")
        b = os.path.join(project_dir, "tests", "testfile2")
        expect_diff = [
            "-This file should not changed",
            "+This file should not changed too"
        ]
        self.assertEqual(cct.diff(a, b), expect_diff)

    def test_diff_force_str(self):
        a = os.path.join(project_dir, "tests", "testfile")
        b = os.path.join(project_dir, "tests", "testfile2")
        self.assertTrue("-{}".format(a) in cct.diff(a, b, force_str=True))

    def test_update_file(self):
        url = "https://github.com/kyan001/PyConsoleCMDTools/raw/main/tests/testfile"
        filepath = os.path.join(project_dir, "tests", "testfile")
        result = cct.update_file(filepath, url)
        expect = "testfile is already up-to-date."
        self.assertFalse(result)
        self.assertTrue(expect in self.fakeout.readline())

    def test_read_file(self):
        filepath = os.path.join(project_dir, "tests", "testfile")
        content = cct.read_file(filepath)
        self.assertEqual(content, "This file should not changed\n")

    def test_ajax_get(self):
        url = "https://yesno.wtf/api"
        param = {"force": "yes"}
        result = cct.ajax(url, param, "get")
        answer = result.get("answer")
        self.assertEqual(answer, "yes")


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)  # print more info, no sys.exit() called.
