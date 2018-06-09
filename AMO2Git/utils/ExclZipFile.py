import re
from pathlib import Path
from zipfile import ZipFile


class ExclZipFile(ZipFile):
	def _exclReParts(exclusions):
		for excl in exclusions:
			if isinstance(excl, Path):
				if not excl.is_absolute():
					yield re.escape(str(excl))
				else:
					raise ValueError("Paths must be relative")
			elif isinstance(excl, str):
				yield excl
			else:
				raise ValueError("Unsupported exclusion type " + type(excl).__name__)

	def _buildExclRe(exclusions):
		return re.compile("^(?:(?:\.\/)*(?:\.\.\/.+)*)*(?:" + "|".join(("(?:" + p + ")" for p in __class__._exclReParts(exclusions))) + ")(?:/.+)?")

	def extractExcl(self, excls, *args, **kwargs):
		_exclsRe = self.__class__._buildExclRe(excls)

		for n in self.namelist():
			if not _exclsRe.match(n):
				self.extract(n, *args, **kwargs)
