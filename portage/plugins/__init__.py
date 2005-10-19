# Copyright: 2005 Gentoo Foundation
# Author(s): Brian Harring (ferringb@gentoo.org)
# License: GPL2
# $Id:$

# I don't like this.
# doesn't seem clean/right.

import os
from portage.const import plugins_dir
from portage.util.fs import FsLock, ensure_dirs, NonExistant
from portage.os_data import portage_gid, root_uid
from ConfigParser import RawConfigParser

PLUGINS_EXTENSION = ".plugins"

class RegistrationException(Exception):
	def __init__(self, reason):		self.reason = reason
	def __str__(self):	return "failed action due to %s" % self.reason
	
class FailedDir(RegistrationException):
	pass
	
class PluginExistsAlready(RegistrationException):
	def __init__(self):
		RegistrationException.__init__(self, "plugin exists aleady, magic found")

class FailedUpdating(RegistrationException):
	def __str__(self):
		return "failed updating plugin_type due error: %s" % (self.reason)

class PluginNotFound(RegistrationException):
	def __init__(self, plugin, reason="unknown"):
		self.plugin, self.reason = plugin, reason
	def __str__(self):
		return "Plugin '%s' wasn't found; reason: %s" % (self.plugin, self.reason)


class GlobalPluginRegistry(object):
	def register(self, plugin_type, magic, version, namespace, replace=False):

		if not ensure_dirs(plugins_dir, uid=root_uid, gid=portage_gid, mode=0755):
			raise FailedDir("Failed ensuring base plugins dir")

		# this could be fine grained down to per plugin_type
		plug_lock = FsLock(plugins_dir)
		plug_lock.acquire_write_lock()
		try:
			ptype_fp = os.path.join(plugins_dir, plugin_type.lstrip(os.path.sep) + PLUGINS_EXTENSION)
			existing = self.query_plugins(plugin_type, locking=False, raw=True)
			if existing.has_section(magic):
				if not replace:
					raise PluginExistsAlready()
				existing.remove_section(magic)
			existing.add_section(magic)
			existing.set(magic, "version", version)
			existing.set(magic, "namespace", namespace)
			try:
				f = open(ptype_fp, "w")
				os.chmod(ptype_fp, 0644)
				os.chown(ptype_fp, root_uid, portage_gid)
				existing.write(f)
				f.close()
			except OSError, oe:
				raise FailedUpdating(oe)

		finally:
			plug_lock.release_write_lock()
	
	def deregister(self, plugin_type, magic, version, ignore_errors=False):
		"""plugin_type is the categorization of the plugin
		magic is the magic constant for lookup
		version is the version of the plugin to yank
		ignore_errors controls whether or not an exception is thrown when the plugin isn't found"""
		plug_lock = FsLock(plugins_dir)
		plug_lock.acquire_write_lock()
		try:
			ptype_fp = os.path.join(plugins_dir, plugin_type.lstrip(os.path.sep) + PLUGINS_EXTENSION)
			existing = self.query_plugins(locking=False, raw=True)
			if plugin_type not in existing:
				if ignore_errors:	return
				raise PluginNotFound(magic, "no plugin type")

			existing = existing[plugin_type]
			if not existing.has_section(magic):
				if ignore_errors:	return
				raise PluginNotFound(magic, "magic not found in plugin_type")
				
			if not existing.has_option(magic, "version") or str(version) != existing.get(magic, "version"):
				if ignore_errors: return
				raise PluginNotFound(magic, "version not found in plugin_type")
			
			existing.remove_section(magic)
			try:
				if len(existing.sections()) == 0:
					os.unlink(ptype_fp)
				else:
					f = open(ptype_fp, "w")
					os.chmod(ptype_fp, 0644)
					os.chown(ptype_fp, root_uid, portage_gid)
					existing.write(f)
					f.close()
			except OSError, oe:
				raise FailedUpdating(oe)

		finally:
			plug_lock.release_write_lock()


	def query_plugins(self, plugin_type=None, locking=True, raw=False):
		# designed this way to minimize lock holding time.
		if plugin_type != None:
			ptypes = [plugin_type + PLUGINS_EXTENSION]
		d = {}
		if locking:
			try:
				plug_lock = FsLock(plugins_dir)
			except NonExistant:
				return {}
			plug_lock.acquire_read_lock()
		try:
			if plugin_type == None:
				ptypes = [x for x in os.listdir(plugins_dir) if x.endswith(PLUGINS_EXTENSION) ]
	
			len_exten = len(PLUGINS_EXTENSION)
			for x in ptypes:
				c = RawConfigParser()
				c.read(os.path.join(plugins_dir, x.lstrip(os.path.sep)))
				if raw:
					d[x[:-len_exten]] = c
				else:
					d[x[:-len_exten]] = dict([(y, c.items(y)) for y in c.sections()])
		
		finally:
			if locking:
				plug_lock.release_read_lock()
		if plugin_type != None:
			return d[plugin_type]
		return d


registry = None

def register(*a, **kw):
	"""calls registry.register(*a, **kw).  will instante the class if it's missing"""
	global registry
	if registry == None:
		registry = GlobalPluginRegistry()
	registry.register(*a, **kw)
	
def deregister(*a, **kw):
	"""calls registry.register(*a, **kw).  will instante the class if it's missing"""
	global registry
	if registry == None:
		registry = GlobalPluginRegistry()
	registry.deregister(*a, **kw)

def query_plugins(*a, **kw):
	"""calls registry.query_plugins(*a, **kw).  will instante the class if it's missing"""
	global registry
	if registry == None:
		registry = GlobalPluginRegistry()
	registry.query_plugins(*a, **kw)
