import os
import tempfile
import shutil
from git import Repo
from argparse import ArgumentParser

repo_url = "https://github.com/eliben/pycparser"
tracked_directory = "utils/fake_libc_include"

def main():
    parser = ArgumentParser(description="Fetch fake libc header files (needed for preprocessing source code) from pycparser's repository")
    parser.add_argument("-o", "--output", type=str, help="Output directory to store the fake libc headers (defaults to fake_libc in cwd)", default=os.path.join(os.getcwd(), 'fake_libc'))
    args = parser.parse_args()

    output_dir = args.output
    print("Writing fake libc into:", output_dir)

    try:
        if os.path.isdir(output_dir):
            os.rmdir(output_dir)
    except OSError:
        print("Directory '", output_dir, "' is not empty, cloning is skipped")
        exit(0)

    temp_dir = tempfile.TemporaryDirectory()

    print("Cloning pycparser's fake libc headers ...")
    pycp_repo = Repo.clone_from(repo_url, temp_dir.name, depth=1)
    shutil.copytree(os.path.join(temp_dir.name, tracked_directory), output_dir)
    pycp_repo.close()

    temp_dir.cleanup()

if __name__ == "__main__":
    main()
