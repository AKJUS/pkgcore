# Copyright: 2005 Gentoo Foundation
# Author(s): Brian Harring (ferringb@gentoo.org)
# License: GPL2
# $Id$

import os

class base(object):
	def get_data(self, arg):
		raise NotImplementedError
	get_path = get_data
	
class local_source(base):
	__slots__ = ["path"]

	def __init__(self, path):
		self.path = path


	def get_path(self):
		if os.path.exists(self.path):
			return self.path
		return None

		
	def get_data(self):
		fp = self.get_path(self.path)
		if fp == None:
			return None
		try:
			f = open(fp, "r")
			d = f.read()
			f.close()
			return d 
		except OSError:
			return None
