# Copyright: 2005-2008 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD

"""
exceptions thrown by repository classes.

Need to extend the usage a bit further still.
"""

from pkgcore.exceptions import PkgcoreException


class RepoError(PkgcoreException):
    """General repository error."""

    def __init__(self, err):
        super().__init__(err)
        self.err = err


class InitializationError(RepoError):
    """General repository initialization failure."""

    def __str__(self):
        return f"repo init failed: {self.err}"


class UnsupportedRepo(RepoError):
    """Repository uses an unknown EAPI or is otherwise not supported."""

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def __str__(self):
        return (
            f'{self.repo.repo_id!r} repo: '
            f'unsupported repo EAPI {str(self.repo.eapi)!r}'
        )
