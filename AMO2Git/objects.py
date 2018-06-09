from collections import OrderedDict
from enum import IntFlag

import dateutil
import dateutil.parser

from .api import *
from .utils import H2RequestsSession


class AddonType(IntFlag):
	extension = 0
	theme = 1
	dictionary = 2


class ExtensionType(IntFlag):
	xul = 0
	restartless = 1
	WebExtension = 2


def langSelector(field, langs=("en-US", "en")):
	try:
		for l in langs:
			if l in field:
				return field["en-US"]
		else:
			return next(iter(field.values()))
	except:
		return ""


class SlotsRepr:
	__slots__ = tuple()

	def __init__(self):
		for cls in self.__class__.mro():
			if cls == __class__:
				break
			for k in cls.__slots__:
				setattr(self, k, None)

	def __slotsNamesIter__(self):
		for cls in self.__class__.mro():
			if hasattr(cls, "__slots__"):
				for k in cls.__slots__:
					yield k

	def __repr__(self):
		return self.__class__.__name__ + "<" + ", ".join((repr(k) + "=" + repr(getattr(self, k)) for k in self.__slotsNamesIter__() if k[0] != "_")) + ">"


class AMOApiItem(SlotsRepr):
	__slots__ = ("_dic", "_id")

	def __init__(self, dic: dict):
		super().__init__()
		self._dic = dic
		self._id = dic["id"]


class Addon(AMOApiItem):
	__slots__ = ("_authors", "_versions", "name", "homepage", "email", "_type", "_supportURI")

	def __init__(self, dic: dict):
		if isinstance(dic, (int, str)):
			dic = getAddonInfo(dic)

		super().__init__(dic)
		self._authors = [Author(a) for a in dic["authors"]]
		for a in self._authors:
			a.retrieveAdditional()
		self.name = langSelector(self._dic["name"])
		self.homepage = langSelector(self._dic["homepage"])
		self.email = langSelector(self._dic["support_email"])
		self._supportURI = langSelector(self._dic["support_url"])
		self._dic["tags"] = set(self._dic["tags"])
		self._dic["_type"] = getattr(AddonType, self._dic["type"])
		self._versions = None

	@property
	def tags(self):
		return self._dic["tags"]

	def retrieveVersions(self):
		self._versions = addonVersions(self)

	@property
	def description(self):
		return langSelector(self._dic["description"])

	@property
	def summary(self):
		return langSelector(self._dic["summary"])

	@property
	def developerComments(self):
		return langSelector(self._dic["developer_comments"])

	@property
	def icon(self):
		return self._dic["icon_url"]


def addonVersions(addon: (Addon, str, int)):
	if isinstance(addon, Addon):
		addonId = addon._id
	else:
		addonId = addon
		addon = None

	res = OrderedDict()
	for v in getVersions(addonId):
		v = AddonVersion(v, addon)
		res[v.version] = v

	return res


class Author(AMOApiItem):
	__slots__ = ("name", "username", "homepage", "location", "occupation", "_biography", "_avatar")

	def __init__(self, dic: dict, email=None):
		if isinstance(dic, (int, str)):
			dic = getAuthorInfo(dic)
		super().__init__(dic)
		self.name = dic["name"]

	def retrieveAdditional(self):
		additionalInfo = getAuthorInfo(self._id)
		if not additionalInfo["has_anonymous_username"]:
			self.username = additionalInfo["username"]
		self.homepage = additionalInfo["homepage"]
		self.location = additionalInfo["location"]
		self._biography = additionalInfo["biography"]
		self._avatar = additionalInfo["picture_url"]


class AddonVersion(AMOApiItem):
	__slots__ = ("_dic", "_addon", "version", "files")

	def __init__(self, dic: dict, addon=None):
		if isinstance(dic, (int, str)):
			if addon:
				if isinstance(addon, (int, str)):
					addonId = addon
				else:
					addonId = addon._id
				dic = getVersion(addonId, dic)
			else:
				raise ValueError("Provide the Addon")
		super().__init__(dic)
		self._addon = addon
		self.version = dic["version"].replace("-signed", "")
		self.files = [AddonFile(f, self) for f in dic["files"]]

	@property
	def releaseNotes(self):
		return langSelector(self._dic["release_notes"])

	@property
	def licenseText(self):
		try:
			return langSelector(self._dic["license"]["text"])
		except:
			return ""

	@property
	def licenseName(self):
		try:
			return langSelector(self._dic["license"]["name"])
		except:
			return ""


class AddonFile(AMOApiItem):
	__slots__ = ("_dic", "_version", "platform", "extType", "created", "uri")

	def __init__(self, dic: dict, version=None):
		if isinstance(dic, (int, str)):
			raise ValueError("This dict is contained in a Version and cannot be fetched by ID")
		super().__init__(dic)
		self._version = version
		self.extType = ExtensionType(ExtensionType.restartless * (not dic["is_restart_required"]) | ExtensionType.WebExtension * dic["is_webextension"])
		self.created = dateutil.parser.isoparse(dic["created"])
		self.platform = dic["platform"]
		self.uri = dic["url"]
