import git
from rich import console, progress
import sys
import os
import shutil
import json
import argparse

# Credit: https://stackoverflow.com/questions/51045540/python-progress-bar-for-git-clone


class Progressbar(git.RemoteProgress):
	OP_CODES = [
		"BEGIN",
		"CHECKING_OUT",
		"COMPRESSING",
		"COUNTING",
		"END",
		"FINDING_SOURCES",
		"RECEIVING",
		"RESOLVING",
		"WRITING",
	]
	OP_CODE_MAP = {
		getattr(git.RemoteProgress, _op_code): _op_code for _op_code in OP_CODES
	}

	def __init__(self) -> None:
		super().__init__()
		self.progressbar = progress.Progress(
			progress.SpinnerColumn(),
			# *progress.Progress.get_default_columns(),
			progress.TextColumn("[progress.description]{task.description}"),
			progress.BarColumn(),
			progress.TextColumn(
				"[progress.percentage]{task.percentage:>3.0f}%"),
			"eta",
			progress.TimeRemainingColumn(),
			progress.TextColumn("{task.fields[message]}"),
			console=console.Console(),
			transient=False,
		)
		self.progressbar.start()
		self.active_task = None

	def __del__(self) -> None:
		# logger.info("Destroying bar...")
		self.progressbar.stop()

	@classmethod
	def get_curr_op(cls, op_code: int) -> str:
		"""Get OP name from OP code."""
		# Remove BEGIN- and END-flag and get op name
		op_code_masked = op_code & cls.OP_MASK
		return cls.OP_CODE_MAP.get(op_code_masked, "?").title()

	def update(
		self,
		op_code: int,
		cur_count: str | float,
		max_count: str | float | None = None,
		message: str | None = "",
	) -> None:
		# Start new bar on each BEGIN-flag
		if op_code & self.BEGIN:
			self.curr_op = self.get_curr_op(op_code)
			# logger.info("Next: %s", self.curr_op)
			self.active_task = self.progressbar.add_task(
				description=self.curr_op,
				total=max_count,
				message=message,
			)

		self.progressbar.update(
			task_id=self.active_task,
			completed=cur_count,
			message=message,
		)

		# End progress monitoring on each END-flag
		if op_code & self.END:
			# logger.info("Done: %s", self.curr_op)
			self.progressbar.update(
				task_id=self.active_task,
				message=f"[bright_black]{message}",
			)


class cloneRepo:
	def clone(url):
		package = url.split('/')[-1]

		if os.path.isdir(package) and len(os.listdir(package)) != 0:
			answer = input(f"Repository {package} already exists. Would you like to remove the directory? (Y/n) ")
			if answer == 'Y' or answer == 'y' or answer == '':
				shutil.rmtree(package)
			elif answer == 'n':
				return

		print(f"Cloning {package}")

		git.Repo.clone_from(
			url=url,
			to_path=url.split('/')[-1],
			progress=Progressbar()
		)


class readJsonFile:
	def getPackageNames(jsonfile):
		try:
			with open(jsonfile) as f:
				data = json.load(f)
				packages = data['packages']

				return packages
		except FileNotFoundError as err:
			err = f"{err}".split("'")
			print(f'File {err[1]} not found. Aborting now')
			sys.exit(1)

	def getTags(devFile, pubFile):
		packages = readJsonFile.getPackageNames(devFile)
		packages2 = {}
		for package in packages:
			tagsPreSplit = []
			tags = []
			cloneRepo.clone(packages[package]['repo'])
			with open(f'{package}/.git/packed-refs', 'r') as f:
				lines = f.readlines()

				for line in lines:
					line = line.strip()
					line = line.split(' ')

					if len(line) < 2:
						continue
					else:
						tagsPreSplit.append(line[1])

			for line in tagsPreSplit[2:]:
				line = line.split('/')
				tags.append(line[2])
			packages2[package] = {
				"vcs": packages[package]['vcs'],
				"repo": packages[package]['repo'],
				"versions": tags,
				"tarball": f"{packages[package]['repo']}/tarball/refs/tags/%%release%%"
			}

		pkg = {
			"packages": packages2
		}
		
		with open(pubFile, "w") as f:
			f.write(json.dumps(pkg, indent=4))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate repositories for the Ascent Package Manager")
	parser.add_argument('-d', '--dev', dest="dev", help="Path to repo-dev.json", required=True)
	parser.add_argument('-p', '--public', dest="pub", help="Path to repo-pub.json", required=True)

	args = parser.parse_args()

	readJsonFile.getTags(args.dev, args.pub)
