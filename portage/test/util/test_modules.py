# Copyright: 2005 Gentoo Foundation
# License: GPL2
# $Id:$


from twisted.trial import unittest

import os
import sys
import shutil
import tempfile

from portage.util import modules


class ModulesTest(unittest.TestCase):

    def setUp(self):
        # set up some test modules for our use
        self.dir = tempfile.mkdtemp()
        packdir = os.path.join(self.dir, 'mod_testpack')
        os.mkdir(packdir)
        # create an empty file
        open(os.path.join(packdir, '__init__.py'), 'w').close()
        for dir in [self.dir, packdir]:
            for i in range(3):
                testmod = open(os.path.join(dir, 'mod_test%s.py' % i), 'w')
                testmod.write('def foo(): pass\n')
                testmod.close()
        
        # append them to path
        sys.path.insert(0, self.dir)

    def tearDown(self):
        # pop the test module dir from path
        sys.path.pop(0)
        # and kill it
        shutil.rmtree(self.dir)
        # make sure we don't keep the sys.modules entries around
        for i in range(3):
            sys.modules.pop('mod_test%s' % i, None)
            sys.modules.pop('mod_testpack.mod_test%s' % i, None)
        sys.modules.pop('mod_testpack', None)
    
    def test_load_module(self):
        # force an exception to make sure the locking doesn't lock up
        self.assertRaises(TypeError, modules.load_module, None)
        # import an already-imported module
        self.assertIdentical(
            modules.load_module('portage.util.modules'), modules)
        # and a system one, just for kicks
        self.assertIdentical(modules.load_module('sys'), sys)
        # non-existing module from an existing package
        self.assertRaises(
            modules.FailedImport, modules.load_module, 'portage.__not_there')
        # (hopefully :) non-existing top-level module/package
        self.assertRaises(
            modules.FailedImport, modules.load_module, '__not_there')
        # unimported toplevel module
        modtest1 = modules.load_module('mod_test1')
        import mod_test1
        self.assertIdentical(mod_test1, modtest1)
        # unimported in-package module
        packtest1 = modules.load_module('mod_testpack.mod_test1')
        import mod_testpack
        from mod_testpack import mod_test1
        self.assertIdentical(mod_test1, packtest1)
        
    def test_load_attribute(self):
        # already imported
        self.assertIdentical(modules.load_attribute('sys.path'), sys.path)
        # unimported
        myfoo = modules.load_attribute('mod_testpack.mod_test2.foo')
        from mod_testpack.mod_test2 import foo
        self.assertIdentical(foo, myfoo)
        # nonexisting attribute
        self.assertRaises(
            modules.FailedImport,
            modules.load_attribute, 'portage.froznicator')
        # nonexisting top-level
        self.assertRaises(
            modules.FailedImport, modules.load_attribute,
            'spork_does_not_exist.foo')
        # not an attr
        self.assertRaises(
            ValueError, modules.load_attribute, 'sys')
        # not imported yet
        self.assertRaises(
            modules.FailedImport,
            modules.load_attribute, 'mod_testpack.mod_test3')
