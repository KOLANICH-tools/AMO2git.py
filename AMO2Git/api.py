from .utils.H2RequestsSession import *

API_BASE = "https://addons.mozilla.org/api/v4"


def getAddonInfoURI(addonID: (str, int)):
	return API_BASE + "/addons/addon/" + str(addonID)


def getVersionsURI(addonID: (str, int)):
	"""(int:addon_id|string:addon_slug|string:addon_guid)"""
	return getAddonInfoURI(addonID) + "/versions/"


def getVersionURI(addonID: (str, int), versionId: (str, int)):
	"""(int:addon_id|string:addon_slug|string:addon_guid)"""
	return getVersionsURI(addonID) + "/" + str(versionId) + "/"


def getAuthorInfoURI(userID: (str, int)):
	"""(int:user_id|string:username)"""
	return API_BASE + "/accounts/account/" + str(userID) + "/"


sess = H2RequestsSession()


def pagination(initialURI: (str, int)):

	t = sess.get(initialURI + "?&page_size=" + str(1 << 63)).json()
	res = []
	res.extend(t["results"])
	while t["next"]:
		print(t["next"])
		t = sess.get(t["next"]).json()
		res.append(t)
	return res


def getVersions(addonID: (str, int)):
	return pagination(getVersionsURI(addonID))


def getVersion(addonID: (str, int), versionId: (str, int)):
	return sess.get(getVersionURI(addonID)).json()


def getAddonInfo(addonID: (str, int)):
	return sess.get(getAddonInfoURI(addonID)).json()


def getAuthorInfo(authorId: (str, int)):
	return sess.get(getAuthorInfoURI(authorId)).json()
