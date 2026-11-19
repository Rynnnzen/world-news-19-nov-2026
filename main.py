#!/usr/bin/env python3
"""World News — 19 November 2026: entry program.

This program ships the front-page image for the make.fun
news-image-20261119 bounty. It does not draw anything and it does not
fetch anything: the finished image already lives in this repository
under ``assets/entry.png``, and this program simply copies it, byte
for byte, into the output directory as ``entry.png``.

Why a copy instead of a drawing? The picture is a composed front
page — masthead, four illustrated news panels, footer ticker — that
was rendered once and checked by hand. Re-drawing it at run time
would only risk changing a pixel, so the program treats the shipped
file as the source of truth and reproduces it exactly.

The program runs with no network, no clock and no randomness, using
only the Python standard library, so every run writes the same
bytes. It writes to ``/output`` by default; set the
``MAKEFUN_OUTPUT_DIR`` environment variable (or pass
``--output-dir``) to point it somewhere else.
"""

import argparse
import hashlib
import os
import shutil
import sys

# The image this entry is about: Thursday 19 November 2026, one
# front page, four stories, in a single 1024x1024 picture.
SOURCE_FILENAME = "entry.png"
ASSETS_DIRNAME = "assets"

# The kit caps an entry at 1 MiB; refuse to write anything larger
# rather than hand the grader a file it would reject outright.
MAX_ENTRY_BYTES = 1_048_576

# A PNG starts with these eight bytes; a JPEG starts with FF D8 FF.
# The kit tells the two apart by their first bytes, so check the
# shipped file is really an image before copying it.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"

DEFAULT_OUTPUT_DIR = "/output"


def script_dir():
    """Directory holding this script (and therefore the assets)."""
    return os.path.dirname(os.path.abspath(__file__))


def source_path():
    """Absolute path of the shipped front-page image."""
    return os.path.join(script_dir(), ASSETS_DIRNAME, SOURCE_FILENAME)


def parse_args(argv):
    """Command-line options; the environment variable is the fallback."""
    parser = argparse.ArgumentParser(
        description="Copy the 19 November 2026 front page to the output directory."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="where to write entry.png (default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    return parser.parse_args(argv)


def resolve_output_dir(args):
    """Pick the output directory: flag first, then environment, then default."""
    if args.output_dir:
        return args.output_dir
    return os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def sha256_of(path):
    """SHA-256 of a file, read in chunks so large files stay cheap."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_source(path):
    """Make sure the shipped file exists, is an image, and fits the cap."""
    if not os.path.isfile(path):
        raise FileNotFoundError("shipped image not found: %s" % path)
    size = os.path.getsize(path)
    if size > MAX_ENTRY_BYTES:
        raise ValueError(
            "shipped image is %d bytes, over the 1 MiB cap" % size
        )
    with open(path, "rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if not (head.startswith(PNG_MAGIC) or head.startswith(JPEG_MAGIC)):
        raise ValueError("shipped file is not a PNG or JPEG image: %s" % path)
    return size


def write_entry(source, output_dir):
    """Copy the shipped image to <output_dir>/entry.png, verifying it.

    The copy lands in a temporary file first and is only moved into
    place once its hash matches the source, so a failed or
    interrupted run never leaves a half-written entry.png behind.
    """
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, SOURCE_FILENAME)
    if os.path.abspath(output_dir) == os.path.abspath(
        os.path.join(script_dir(), ASSETS_DIRNAME)
    ):
        raise ValueError("refusing to write over the shipped image")
    staging = destination + ".tmp"
    try:
        shutil.copyfile(source, staging)
        if sha256_of(staging) != sha256_of(source):
            raise ValueError("staged copy does not match the shipped image")
        os.replace(staging, destination)
    finally:
        if os.path.exists(staging):
            os.remove(staging)
    if sha256_of(destination) != sha256_of(source):
        raise ValueError("output does not match the shipped image")
    return destination


def main(argv=None):
    """Copy the front page and report what was written."""
    args = parse_args(argv)
    source = source_path()
    size = check_source(source)
    output_dir = resolve_output_dir(args)
    destination = write_entry(source, output_dir)
    print(
        "wrote %s (%d bytes, sha256 %s)"
        % (destination, size, sha256_of(destination))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
