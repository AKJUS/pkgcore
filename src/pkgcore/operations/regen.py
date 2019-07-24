# Copyright: 2011 Brian Harring <ferringb@gmail.com>
# License: GPL2/BSD 3 clause

import queue

from snakeoil.compatibility import IGNORED_EXCEPTIONS

from pkgcore.util.thread_pool import map_async


def regen_iter(iterable, regen_func, observer):
    for pkg in iterable:
        try:
            regen_func(pkg)
        except IGNORED_EXCEPTIONS as e:
            if isinstance(e, KeyboardInterrupt):
                return
            raise
        except Exception as e:
            yield pkg, e


def regen_repository(repo, pkgs, observer, threads=1, pkg_attr='keywords', **kwargs):
    helpers = []

    def _get_repo_helper():
        if not hasattr(repo, '_regen_operation_helper'):
            return lambda pkg: getattr(pkg, 'keywords')
        # for an actual helper, track it and invoke .finish if it exists.
        helper = repo._regen_operation_helper(**kwargs)
        helpers.append(helper)
        return helper

    def get_args():
        return (_get_repo_helper(), observer)

    errors = queue.Queue()
    map_async(pkgs, errors, regen_iter, threads=threads, per_thread_args=get_args)

    # release ebuild processors
    for helper in helpers:
        f = getattr(helper, 'finish', None)
        if f is not None:
            f()

    # yield any errors that occurred during metadata generation
    while not errors.empty():
        yield errors.get()
