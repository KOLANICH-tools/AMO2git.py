import re

from .CommandsGenerator import *


def genDownloadCommand(uris, destFolder, streamsCount=32, type="aria2"):
	streamsCount = str(streamsCount)

	if type == "aria2":
		return " ".join(("(\n" + "\n".join((commandGen.echo(uri) for uri in uris)) + "\n)", "|", "aria2c", "--continue=true", "--enable-mmap=true", "--optimize-concurrent-downloads=true", "-j", streamsCount, "-x 16", "-d", str(destFolder), "--input-file=-"))
	else:
		args = ["curl", "-C", "-", "--location", "--remote-name", "--remote-name-all", "--xattr"]
		args.extend(uris)
		return " ".join(args)


mozillaAddonUri = re.compile("https?://addons.mozilla.org/(?:[^\/]+/)?(?:[^\/]+/)?addon/([^\/]+)/.+")


def AMOUri2ID(uri: str):
	return mozillaAddonUri.match(uri).group(1)
