import re

from tqdm import tqdm

from . import *
from .utils import AMOUri2ID

APP_NAME = "AMO2git"

from plumbum import cli


class AMO2GitCLI(cli.Application):
	"""The main command"""


@AMO2GitCLI.subcommand("retrieve")
class AMO2GitRetriever(cli.Application):
	"""Creates a script to download all the versions of addons using aria2c"""

	streamsCount = cli.SwitchAttr("--streamsCount", int, default=32, help="Max count of streams")
	versionsFolder = cli.SwitchAttr("--versionsFolder", cli.switches.MakeDirectory, default=None, help="A dir to save addons. Must be large enough.")

	def main(self, addonID: str = "noscript"):
		try:
			addonID = AMOUri2ID(addonID)
		except:
			pass

		uris = []
		versions = addonVersions(addonID)

		if not self.versionsFolder:
			self.versionsFolder = addonID + "-downloads"

		self.versionsFolder = Path(self.versionsFolder)

		for ver in versions.values():
			for f in ver.files:
				uris.append(f.uri)
		print(genDownloadCommand(uris, self.versionsFolder, self.streamsCount))


@AMO2GitCLI.subcommand("convert")
class AMO2GitConverter(cli.Application):
	"""Converts predownloaded versions of the addon into a git history"""

	versionsFolder = cli.SwitchAttr("--versionsFolder", cli.switches.ExistingDirectory, default=None, help="A dir to save addons. Must contain all the versions needed.")
	repoFolder = cli.SwitchAttr("--repoFolder", cli.switches.MakeDirectory, default=None, help="A dir to have a git repo. Must be large enough.")
	authorEmail = cli.SwitchAttr("--email", str, default=None, help="A email to use for commits")
	commiterName = cli.SwitchAttr("--commiterName", str, default=AddonFileTransformer.APP_NAME, help="A name to use for a commiter of commits")
	commiterEmail = cli.SwitchAttr("--commiterEmail", str, default=None, help="A email to use for a commiter of commits")

	def main(self, addonID: (str, int)):
		try:
			addonID = AMOUri2ID(addonID)
		except:
			pass

		addon = Addon(addonID)
		addon.retrieveVersions()

		if not self.versionsFolder:
			self.versionsFolder = addonID + "-downloads"

		if not self.repoFolder:
			self.repoFolder = addonID + "-repo"

		self.versionsFolder = Path(self.versionsFolder)
		self.repoFolder = Path(self.repoFolder)

		if self.commiterEmail is not None:
			commiter = GitName(self.commiterName, self.commiterEmail)
		else:
			commiter = self.commiterName

		tr = AddonFileTransformer(addon, self.repoFolder, self.versionsFolder, authorEmail=self.authorEmail, commiter=commiter)

		progressIter = tr.transform()
		progress = next(progressIter)
		pr = progress.processed

		with tqdm(total=progress.total) as pb:

			def processProgress(progress, pr):
				pb.total = progress.total
				pb.desc = progress.version
				if progress.message:
					pb.write(progress.message)
				pb.update(progress.processed - pr)
				return progress.processed

			pr = processProgress(progress, pr)
			for progress in progressIter:
				pr = processProgress(progress, pr)


if __name__ == "__main__":
	AMO2GitCLI.run()
