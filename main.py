"""Copy the finished front-page graphic into the harness output folder.

The artwork is already complete and ships in this repo as
assets/entry.png. This script does nothing but place an exact copy of it
in the output directory under the same name, entry.png, so the harness
can find it. It needs no network, no extra packages, and no randomness:
every run produces the same bytes as the file in the repo.

The output directory is /output by default and can be pointed elsewhere
with the MAKEFUN_OUTPUT_DIR environment variable.
"""

import os
import shutil


def bundled_image_path():
    """Return the absolute path of the image shipped with this repo."""
    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(here, "assets", "entry.png")


def output_directory():
    """Return the output directory, creating it when it does not exist."""
    directory = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(directory, exist_ok=True)
    return directory


def main():
    shutil.copyfile(bundled_image_path(), os.path.join(output_directory(), "entry.png"))


if __name__ == "__main__":
    main()
