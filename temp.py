import ctypes
so = ctypes.CDLL("libtest.so")
so.display()
