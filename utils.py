from config import IS_TEST


class Log:
    def __init__(self, print_count=0):
        self.print_count = print_count
        self.log_info = []

    def log(self, *info):
        self.log_info.append(" ".join(info))
        if self.print_count != 0 and len(self.log_info) == self.print_count:
            print("\n".join(self.log_info))
            self.log_info.clear()

    def close(self):
        if len(self.log_info) > 0:
            print("\n".join(self.log_info).replace("\n\b", ""))


_log = Log()


def log(*info):
    if IS_TEST:
        _log.log(*info)


def log_close():
    _log.close()


def switch_func(condition, func1, func1_args, fun2, fun2_args):
    if type(func1_args) is not tuple:
        func1_args = tuple([func1_args])
    if type(fun2_args) is not tuple:
        fun2_args = tuple([fun2_args])
    if condition:
        func1(*func1_args)
    else:
        fun2(*fun2_args)
