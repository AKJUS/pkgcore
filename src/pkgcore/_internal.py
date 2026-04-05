__all__ = ("deprecated",)
from snakeoil.deprecation import Registry

from pkgcore import __python_mininum_version__, __version_info__

deprecated = Registry(
    "pkgcore",
    version=__version_info__,
    python_mininum_version=__python_mininum_version__,
)
