import consoleiotools as cit
import consolecmdtools as cct


def inspect(func_name, *args, **kwargs):
    cit.br()
    args_txt = ""
    if args:
        args_txt += ", ".join(f"{('`' + a + '`') if isinstance(a, str) else str(a)}" for a in args)
    if kwargs:
        args_txt += ", " + ", ".join(f"{k}=" + f"{('`' + v + '`') if isinstance(v, str) else str(v)}" for k, v in kwargs.items())
    cit.print(f"[dim bright_white]# {func_name}({args_txt})")
    return getattr(cct, func_name)(*args, **kwargs)


def examples():
    inspect("clear_screen")
    cit.print(inspect("banner", "This is a banner"))
    cit.print(inspect("md5", "blah blah blah"))
    cit.print(inspect("md5", 42))
    cit.print(inspect("md5", "README.md"))
    cit.print(inspect("md5", "README.md", force_text=True))
    cit.print(inspect("crc32", "blah blah blah"))
    cit.print(inspect("crc32", 42))
    cit.print(inspect("crc32", "README.md"))
    cit.print(inspect("crc32", "README.md", force_text=True))
    cit.print(inspect("get_py_cmd"))
    inspect("run_cmd", "echo hello")
    cit.print(inspect("read_cmd", "echo hello"))
    cit.print(inspect("is_cmd_exist", "ls"))
    cit.print(inspect("get_dir", "README.md"))
    cit.print(inspect("get_dir", "README.md", mode="file"))
    cit.print(inspect("get_dir", "README.md", mode="basename"))
    for line in inspect("diff", "str 1", "str 2"):
        cit.print(line)
    for line in inspect("diff", "str 1", "str 2", meta=True):
        cit.print(line)
    for line in inspect("diff", ["a", "b"], ["a", "b", "c"]):
        cit.print(line)
    for line in inspect("diff", ["a", "b"], ["a", "b", "c"], context=2):
        cit.print(line)
    resp = inspect("ajax", "https://yesno.wtf/api", method="get")
    cit.print(resp)
    cit.print(inspect("main_color", resp["image"], is_url=True))
    cit.print(inspect("read_file", "README.md")[:19])
    cit.print(inspect("is_admin"))


if __name__ == "__main__":
    cit.panel(f"cct.__version__ = {cct.__version__}", title="ConsoleCMDTools Features")
    examples()
