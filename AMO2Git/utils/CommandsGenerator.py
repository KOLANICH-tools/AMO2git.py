import platform
import re
import shlex


class CommandsGenerator:
	def quote(self, input: str):
		return shlex.quote(str(input))

	def echo(self, input: str):
		return "echo " + shlex.quote(str(input))


specChar = re.compile("\\W")


class CommandsGeneratorWin(CommandsGenerator):
	"""A class to create shell commands. Create another class for other platforms"""

	def echo(self, input: str):
		return "echo " + specChar.subn("^\\g<0>", input)[0]

	def quote(self, input: str):
		# shlex.quote works incorrectly on Windows
		return '"' + str(input).replace('"', '""') + '"'


if platform.system() == "Windows":
	commandGen = CommandsGeneratorWin()
else:
	commandGen = CommandsGenerator()
