import itertools
import os

from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_source("libfast5mod",
    r"""
    #include "unint8str.h"

    """,
    include_dirs=['src'],
    sources=[os.path.join('src', x) for x in ('unint8str.c',)],
    extra_compile_args=['-std=c99', '-msse3', '-O3'],
)

cdef = []
for header in ('unint8str.h',):
    with open(os.path.join('src', header), 'r') as fh:
        # remove directives
        lines = ''.join(x for x in fh.readlines() if not x.startswith('#'))
        cdef.append(lines)

ffibuilder.cdef('\n\n'.join(cdef))

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
