# Copyright: 2005 Gentoo Foundation
# Author(s): Brian Harring (ferringb@gentoo.org)
# License: GPL2
# $Id: flat_list.py 1911 2005-08-25 03:44:21Z ferringb $

import fs_template
import cache_errors
import os, stat

# store the current key order *here*.
class database(fs_template.FsBased):

	autocommits = True

	def __init__(self, *args, **config):
		super(database,self).__init__(*args, **config)
		self.location = os.path.join(self.location, 
			self.label.lstrip(os.path.sep).rstrip(os.path.sep))

		if not os.path.exists(self.location):
			self._ensure_dirs()


	def _getitem(self, cpv):
		try:
			myf = open(os.path.join(self.location, cpv),"r")
			d = dict(map(lambda x:x.rstrip().split("=", 1), myf))
		except IOError:
			raise KeyError(cpv)
		except OSError, e:
			raise cache_errors.CacheCorruption(cpv, e)

		try:	d["_mtime_"] = os.fstat(myf.fileno()).st_mtime
		except OSError, e:	
			myf.close()
			raise cache_errors.CacheCorruption(cpv, e)
		myf.close()
		for x in self._known_keys:
			if x not in d:
				d[x] = ''
		return d


	def _setitem(self, cpv, values):
		s = cpv.rfind("/")
		fp = os.path.join(self.location,cpv[:s],".update.%i.%s" % (os.getpid(), cpv[s+1:]))
		try:	myf=open(fp, "w")
		except IOError, ie:
			if ie.errno == 2:
				try:
					self._ensure_dirs(cpv)
					myf=open(fp,"w")
				except (OSError, IOError),e:
					raise cache_errors.CacheCorruption(cpv, e)
		except OSError, e:
			raise cache_errors.CacheCorruption(cpv, e)
		
		for k, v in values.items():
			if x != "_mtime_":
				myf.writeline("%s=%s\n" % (k, v))

		myf.close()
		self._ensure_access(fp, mtime=values["_mtime_"])

		#update written.  now we move it.

		new_fp = os.path.join(self.location,cpv)
		try:	os.rename(fp, new_fp)
		except (OSError, IOError), e:
			os.remove(fp)
			raise cache_errors.CacheCorruption(cpv, e)


	def _delitem(self, cpv):
		try:
			os.remove(os.path.join(self.location,cpv))
		except OSError, e:
			if e.errno == 2:
				raise KeyError(cpv)
			else:
				raise cache_errors.CacheCorruption(cpv, e)


	def has_key(self, cpv):
		return os.path.exists(os.path.join(self.location, cpv))


	def iterkeys(self):
		"""generator for walking the dir struct"""
		dirs = [self.location]
		len_base = len(self.location)
		while len(dirs):
			for l in os.listdir(dirs[0]):
				if l.endswith(".cpickle"):
					continue
				p = os.path.join(dirs[0],l)
				st = os.lstat(p)
				if stat.S_ISDIR(st.st_mode):
					dirs.append(p)
					continue
				yield p[len_base+1:]
			dirs.pop(0)

