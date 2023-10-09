import datetime
import re
import tempfile
from collections import OrderedDict
from pathlib import Path, PurePath
from urllib.parse import urlparse
from warnings import warn

import git

from .objects import *
from .utils import *
from .utils.arg import argmin
from .utils.ExclZipFile import *

warn("We have moved from M$ GitHub to https://codeberg.org/KOLANICH-tools/AMO2Git.py , read why on https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo .")

class GitName(git.Actor):
	def __init__(self, name, email=None):
		super().__init__(name, email)

	def __str__(self):
		return name + ((" <" + email + ">") if email else "")


def authorGitName(author, email=None):
	if not email:
		email = author.email
	return GitName(author.name, email)


class ProgressReport:
	__slots__ = ("version", "processed", "total", "message")

	def __init__(self, total: int):
		self.version = ""
		self.processed = 0
		self.total = total
		self.message = ""

	def __repr__(self):
		return self.version + " " + str(self.processed / self.total * 100) + "% " + str(self.message)


def datetime2GitDatetimeString(dt):
	"""gitpython is shit, it doesn't accept datetime, dates parser is badly broken, neither dt.created.ctime(), nor dt.created.isoformat(), had to rely on ugly hacks like this function"""
	return dt.replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()[:-6]


class SlotsDecorator:
	__slots__ = tuple()

	def __init__(self, obj):
		mro = [cls for cls in self.__class__.mro() if cls is not __class__]
		if not hasattr(mro[1], "__slots__"):
			self = obj
			self.__class__ = mro[0]
			#mro[0].__init__(self, *args, **kwargs)
		else:
			for k in dir(obj):
				if not (k[0:2] == "__" and k[-2:] == "__") and not isinstance(getattr(obj.__class__, k), property) and not callable(getattr(obj.__class__, k)):
					setattr(self, k, getattr(obj, k))


class AddonVersionPresentInRepo(SlotsDecorator, AddonVersion):
	__slots__ = ("repoTag",)

	def __init__(self, obj, tag):
		SlotsDecorator.__init__(self, obj)
		self.repoTag = tag


class AddonFileTransformer:
	APP_NAME = "AMO2git"

	def __init__(self, addon, repo, downloadedAddonsDir, commiter: (GitName, str) = None, commitDate=None, tempDirPath: Path = None, authorEmail=None):
		self.addon = addon

		if not authorEmail:
			authorEmail = self.addon.email
		self.authorEmail = authorEmail
		if commiter is None:
			commiter = GitName(self.__class__.APP_NAME, self.authorEmail)
		elif isinstance(commiter, str):
			commiter = GitName(commiter, self.authorEmail)

		self.commiter = commiter

		if commitDate is None:
			commitDate = datetime2GitDatetimeString(datetime.datetime.utcnow())  # shit!
		self.commitDate = commitDate
		self.checkRepo(repo)
		self.downloadedAddonsDir = Path(downloadedAddonsDir)

		if tempDirPath is None:
			self._tempDir = tempfile.TemporaryDirectory(dir=self.downloadedAddonsDir.parent)
			tempDirPath = Path(self._tempDir.name)
		self.tempDirPath = tempDirPath

	versionRx = re.compile("^v(\d.+)")

	def getVersionsFromRepoTags(self):
		versions = OrderedDict()
		for t in self.repo.tags:
			r = self.__class__.versionRx.match(t.name)
			if r:
				versions[r.group(1)] = t
		return versions

	def matchTagsVersionsToAMO(self, versionsAMO, versionsTags):
		for v, vt in versionsTags.items():
			versionsAMO[v] = AddonVersionPresentInRepo(versionsAMO[v], vt)

	def getLastVersionInRepo(self, versionsAMO):
		# shit, it seems that this array is not in chronological order, need to do something!
		try:
			return next(reversed())
		except StopIteration:
			return None

	binaryTypes = ("*.png", "*.jpg", "*.gif", "*.bmp", "*.ico", "*.so", "*.dll", "*.ocx", "*.jar", "*.zip", "*.xpi", "*.mo")
	ignores = ("/META-INF",)

	def checkRepo(self, repo):
		if isinstance(repo, Path):
			self.repoDir = repo
			try:
				self.repo = git.Repo(str(self.repoDir))
			except:
				self.repo = self.initRepo()
		else:
			self.repoDir = Path(repo.working_dir)

	def initRepo(self):
		repo = git.Repo.init(str(self.repoDir))
		repo.git.lfs("track", *__class__.binaryTypes)

		with (self.repoDir / ".gitignore").open("wt", encoding="utf-8") as f:
			for ign in __class__.ignores:
				f.write(ign)
				f.write("\n")
		repo.index.add([".gitignore", ".gitattributes"])
		repo.index.commit("Initialized the repo with some files", author=self.commiter, committer=self.commiter, author_date=self.commitDate, commit_date=self.commitDate, skip_hooks=True)
		repo.git.lfs("post-commit")
		return repo

	def _commit(self, ver, created):
		addon = ver._addon

		# self.repo.index.add(["*"]) #lfs doesn't work this way :(
		self.repo.git.add("*")

		commitMsg = ""
		commitMsg += ver.releaseNotes
		if len(addon._authors) > 1:
			commitMsg += "Authors: " + " ,".join((str(authorGitName(a)) for a in addon._authors))
			authorName = self.commiter
		else:
			authorName = authorGitName(addon._authors[0], self.authorEmail)

		authorDate = datetime2GitDatetimeString(created)
		self.repo.index.commit(commitMsg, author=authorName, committer=self.commiter, author_date=authorDate, commit_date=self.commitDate, skip_hooks=True)
		# a hack for Windows: git lfs setups hooks, but this lib cannot execute them
		self.repo.git.lfs("post-commit")

		if ver and ver.version:
			self.repo.create_tag("v" + ver.version)

	def downloadedFileName(self, addonFile):
		return self.downloadedAddonsDir / PurePath(urlparse(addonFile.uri).path).name

	def checkFile(self, zipArch, rx, defaultFileName, text):
		cands = [f for f in self.repoDir.iterdir() if rx.match(f.name)]
		licFileName = None
		if cands:
			licFileName = cands[0]
		else:
			licFileName = self.repoDir / defaultFileName

		try:
			zf.getinfo(licFileName.name)  # check if present in the arch
		except:
			with licFileName.open("wt", encoding="utf-8") as f:
				f.write(text)

	licenseFileNameRx = re.compile("(?:un)?license|copying(\.(?:md|markdown|a(?:scii)?doc|rst|txt))?", re.I)

	def checkLicense(self, zipArch, addonFile):
		self.checkFile(zipArch, __class__.licenseFileNameRx, "License.txt", addonFile._version.licenseText)

	readmeFileNameRx = re.compile("readme(\.(?:md|markdown|a(?:scii)?doc|rst|txt))?", re.I)

	def checkReadMe(self, zipArch, addonFile):
		addon = addonFile._version._addon
		text = addon.summary + "\n\n" + addon.description + "\n"
		self.checkFile(zipArch, __class__.readmeFileNameRx, "ReadMe.md", text)

	def unpackInternalArchive(self, archiveName, targetDir):
		newArchiveName = self.tempDirPath / archiveName.name
		archiveName.rename(newArchiveName)

		with ExclZipFile(newArchiveName) as zf:
			zf.extractExcl(["\.git"], path=targetDir)
		newArchiveName.unlink()

	def unpackInternalZipArchives(self, targetDir: Path, globExpr: str):
		archives = targetDir.glob(globExpr)
		names = []
		for archiveName in archives:
			self.unpackInternalArchive(archiveName, targetDir)
			names.append(archiveName)
		return names

	def unpackInternalChromeJarsIfAny(self):
		self.unpackInternalZipArchives(self.repoDir / "chrome", "*.jar")

	def unpackInternalExtensionsIfAny(self):
		raise NotImplementedError()

	def getBranchName(extType: ExtensionType):
		# assumming that iteration goes in the order increasing bit position and that xul is 0
		maxType = type(extType)((1 << extType.bit_length()) >> 1)
		return maxType.name

	def createCommit(self, version):
		for addonFile in version.files:
			branchName = self.__class__.getBranchName(addonFile.extType)
			if branchName not in self.repo.heads:
				br = self.repo.create_head(branchName)
				self.repo.head.reference = br
			else:
				br = self.repo.heads[branchName]
				if br is not self.repo.head.reference:
					prevSha = self.repo.head.reference.object.hexsha
					self.repo.head.reference = br

					self.repo.head.reset(index=True, working_tree=True)
					currentSha = self.repo.head.reference.object.hexsha
					self.repo.git.lfs("post-checkout", prevSha, currentSha, "1")  # the hook is not implemented in the lib

			with ExclZipFile(self.downloadedFileName(addonFile)) as zf:
				zf.extractExcl(["\.git", "META[_-]INF"], path=self.repoDir)
				self.checkLicense(zf, addonFile)
				self.checkReadMe(zf, addonFile)
		# TODO: split by platforms
		self.unpackInternalChromeJarsIfAny()

		self._commit(version, max((addonFile.created for addonFile in version.files)))

	def transform(self):
		#self.versions=self.addon._versions.sort(key=lambda v: min(v.files, key=lambda f: f.created).created)
		versions = type(self.addon._versions)(reversed(self.addon._versions.items()))  # AMO returns the versions in the order from the newest to the oldest, and timestamps are not always correct, old versions have the same timestamp

		self.matchTagsVersionsToAMO(versions, self.getVersionsFromRepoTags())

		rep = ProgressReport(len(versions))

		for v in versions.values():
			rep.version = v.version
			if hasattr(v, "repoTag"):
				rep.message = "skipping version: " + v.version
				yield rep
			else:
				rep.message = "commiting version: " + v.version
				yield rep
				self.createCommit(v)
			rep.processed += 1
			rep.message = None
			yield rep
		rep.message = "collecting garbage"
		yield rep
		self.repo.git.gc(aggressive=True)
		rep.message = "Finished"
		yield rep
