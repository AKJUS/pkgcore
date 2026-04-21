"""This is internal, do not use it externally, nor add any further usage of it.

This is a version of tarfile modified strictly for snakeoil.data_sources usage.

This is will be removed once pkgcore and snakeoil data_source usage is removed.
"""

import importlib.util

# force a fresh module import of tarfile that is ours to monkey patch, bypassing sys.modules
#  reuse.
if (spec := importlib.util.find_spec("tarfile")) is None:
    raise ImportError("python bundled tarfile module could not be found for importing")
tarfile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tarfile)
del spec


# add in a tweaked ExFileObject that is usable by snakeoil.data_source
class ExFileObject(tarfile.ExFileObject):
    __slots__ = ()
    exceptions = (EnvironmentError,)


tarfile.fileobject = ExFileObject

# finished monkey patching. now to lift things out of our tarfile
# module into this scope so from/import behaves properly.

locals().update((k, getattr(tarfile, k)) for k in tarfile.__all__)
