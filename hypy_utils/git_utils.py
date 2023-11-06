import datetime
import shlex
from pathlib import Path
from subprocess import check_output
from typing import NamedTuple

import dateutil.parser


class ExtractedCommit(NamedTuple):
    sha: str
    author: str
    email: str
    time: str
    message: str
    file_names: list[str]

    def get_time(self) -> datetime:
        return dateutil.parser.isoparse(self.time)


def git_log(path: Path, fail_silently: bool = False) -> list[ExtractedCommit]:
    """
    Call and parse git log. This function requires that git>=2.37.1 is installed on your system.

    :param path: Path of git repository
    :param fail_silently: If true, ignore errors. If false, raise exception when errors occur.
    :return: List of commits
    """
    # check_call(shlex.split('git config diff.renames 0'))
    cmd = f"git -c 'diff.renamelimit=0' -c 'diff.renames=0' -C '{path.absolute()}' log --name-status --diff-filter=AMD --pretty=format:'START_COMMIT_QwQ %H%n%aN%n%aE%n%aI%n%s%n'"
    log = check_output(shlex.split(cmd)).decode('utf-8', 'ignore')

    def extract_commit(block: str) -> ExtractedCommit:
        try:
            lines = block.split('\n')
            sha, author, email, date, message = lines + [""] if len(lines) == 4 else lines[:5]
            files = [f.replace('\t', '/') for f in lines[6:]]
            return ExtractedCommit(sha, author, email, date, message, files)
        except Exception as e:
            print(f'========== Commit Extract Error {e} ==========\n{block}\n==========')
            if not fail_silently:
                raise e

    return [extract_commit(c.strip()) for c in log.split('START_COMMIT_QwQ') if c]
