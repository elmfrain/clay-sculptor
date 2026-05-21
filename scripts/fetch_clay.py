import os
import tempfile
import shutil
import sys
from git import Repo
from argparse import ArgumentParser, Namespace

repo_url: str = "https://github.com/nicbarker/clay.git"
tracked_files: list[str] = []

def validate_args(parser: ArgumentParser) -> Namespace:
    args = parser.parse_args()
    num_flags = 0

    if args.branch:
        num_flags = num_flags + 1
    if args.commit:
        num_flags = num_flags + 1
    if args.tag:
        num_flags = num_flags + 1

    if num_flags == 0:
        print("You must provide exclusively one of the following flags: (branch, commit, or tag)", file=sys.stderr)
        exit(-1)

    if num_flags != 1:
        print("Too many arguments; You must provide exclusively one of the following flags: (branch, commit, or tag)", file=sys.stderr)
        exit(-1)

    return args

def copy_tracked_files(repo_dir: str, output_dir: str) -> None:
    for file in tracked_files:
        input_file = os.path.join(repo_dir, file)
        output_file = os.path.join(output_dir, file)

        print("Copying '", file, "' into ", output_file)
        os.makedirs(os.path.split(output_file)[0], exist_ok=True)
        shutil.copyfile(input_file, output_file)

def main():
    global tracked_files

    parser = ArgumentParser(description="Fetch Clay's source from its official repository. You must provide exclusively one of the following flags: (branch, commit, or tag)")
    parser.add_argument('tracked_files', type=str, nargs='+', help="Source code files to copy from clay's repo")
    parser.add_argument('-b', '--branch', type=str, help="Select which branch to fetch from")
    parser.add_argument('-c', '--commit', type=str, help="Select which commit to fetch from")
    parser.add_argument('-t', '--tag', type=str, help="Select which tag to fetch from")
    parser.add_argument('-o;', '--output', type=str, help="Output directory of all tracked files from clay's repo", default=os.getcwd())

    args = validate_args(parser)
    tracked_files = args.tracked_files

    output_dir = args.output
    print("Writing clay's source code into:", output_dir)

    temp_dir = tempfile.TemporaryDirectory()

    print("Cloning clay's repository ...")
    if args.branch or args.tag:
        branch = args.branch
        if args.tag:
            branch = args.tag

        branch.strip()
        clay_repo = Repo.clone_from(repo_url, temp_dir.name, branch=branch, depth=1)
        copy_tracked_files(temp_dir.name, output_dir)
        clay_repo.close()

    if args.commit:
        clay_repo = Repo.clone_from(repo_url, temp_dir.name)
        clay_repo.head.reset(commit=args.commit.strip(), index=True, working_tree=True)
        copy_tracked_files(temp_dir.name, output_dir)
        clay_repo.close()

    temp_dir.cleanup()

if __name__ == "__main__":
    main()
