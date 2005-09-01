# Copyright: 2005 Gentoo Foundation
# Author(s): Brian Harring (ferringb@gentoo.org)
# License: GPL2
# $Id:$

import os
from portage.chksum import get_handler
import errors

class fetcher(object):

	def _verify(self, file_location, target, required=None):
		"""internal function for derivatives.
		digs through chksums, and returns:
		-1: iff (size chksum is available, and file is smaller then stated chksum) or file doesn't exist.
		0:  iff all chksums match
		1:  iff file is too large (if size chksums are available) or else size is right but a chksum didn't match.
		
		if required == None, all chksums must match
		"""
		if not os.path.exists(file_location):
			return -1

		handlers = get_handler(*target.chksums.keys())
		if required:
			for x in target.chksums:
				if x not in handlers:
					raise errors.RequiredChksumDataMissing(target, x)
		
		if "size" in handlers:
			c = handlers["size"](file_location, target.chksums["size"], cmp_syntax=True)
			if c != 0:
				return (c < 0 and -1) or 1

		for x in handlers:
			if x != "size" or x not in handlers:
				if not handlers[x](file_location, target.chksums[x]):
					return 1
				
		return 0

	def __call__(self, *a, **kw):
		return self.fetch(*a, **kw)
