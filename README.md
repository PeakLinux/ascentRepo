### Main Repositories for the Ascent Package Manager

genRepo.py is for generating your own repositories. To get started generating your own repositories, first run the following code block to set up the dependencies for genRepo
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
After installing all required dependencies, run `python genRepo.py -d <path to repo-dev.json> -p <path to repo-pub.json>` and let the script take care of the rest

- The structure of a repo-dev.json file is as follows (you can also look in Utilities/repo-dev.json for a full example):
```json
{
	"packages": {
		"pkgname": {
			"vcs": "<vcs (currently only git is supported)>",
			"repo": "<url to source repository>",
			"releaseMethod": "<Type of releases to use (currently only tags are implemented)>",
			"buildSystem": "<buildsystem to use (currently only default (./configure, make, make install) is implemented>"
		}
	}
}
```
