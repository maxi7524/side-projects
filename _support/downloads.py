"""Download declared inputs without tracking datasets in Git."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


def get_custom_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


logger = get_custom_logger(__name__)


def digest(path: Path) -> str:
    """Compute a streaming SHA-256 digest.

    :param path: Input file.
    :returns: Hexadecimal digest.
    """
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def contained(root: Path, relative: str) -> Path:
    """Resolve a path inside a designated project directory.

    :param root: Permitted directory.
    :param relative: Relative resource path.
    :returns: Validated absolute path.
    :raises ValueError: If the path escapes the project directory.
    """
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f"Resource path escapes its project directory: {relative}")
    return path


def retrieve(resource: dict, root: Path, archive: Path | None = None) -> str:
    """Retrieve one input atomically and verify its declared checksum.

    :param resource: Resource metadata, paths, checksums, and retrieval methods.
    :param root: Assignment directory.
    :param archive: Optional preserved migration archive.
    :returns: ``cached``, ``archive``, ``url``, or ``github``.
    :raises ValueError: For an unsafe path or checksum mismatch.
    :raises RuntimeError: If no declared retrieval method succeeds.
    """
    target = contained(root, resource["path"])
    expected = resource.get("sha256")
    if target.is_file() and (expected is None or digest(target) == expected):
        logger.debug("Input already present: %s", target)
        return "cached"
    target.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    # Stage input bytes before replacing the assignment's existing file.
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        methods = []
        if archive and resource.get("archive_path"):
            methods.append(("archive", resource["archive_path"]))
        if resource.get("url"):
            methods.append(("url", resource["url"]))
        if resource.get("github_api"):
            methods.append(("github", resource["github_api"]))
        for kind, source in methods:
            try:
                if kind == "archive":
                    shutil.copyfile(contained(archive, source), temporary)
                elif kind == "url":
                    request = urllib.request.Request(
                        source, headers={"User-Agent": "coursework-data-downloader/1"}
                    )
                    with (
                        urllib.request.urlopen(request, timeout=90) as response,
                        temporary.open("wb") as output,
                    ):
                        if "text/html" in getattr(response, "headers", {}).get(
                            "Content-Type", ""
                        ):
                            raise ValueError(
                                "Source returned an HTML page instead of dataset bytes"
                            )
                        shutil.copyfileobj(response, output)
                else:
                    # REMARK: gh supplies credentials internally; tokens never enter
                    # manifests, command arguments, or logger output.
                    with temporary.open("wb") as output:
                        subprocess.run(
                            [
                                "gh",
                                "api",
                                source,
                                "--header",
                                "Accept: application/vnd.github.raw+json",
                            ],
                            stdout=output,
                            stderr=subprocess.PIPE,
                            check=True,
                        )
                if expected is not None and digest(temporary) != expected:
                    raise ValueError(
                        "Downloaded bytes do not match the declared SHA-256"
                    )
                os.replace(temporary, target)
                logger.info("Prepared input %s", resource["path"])
                return kind
            except (
                OSError,
                ValueError,
                urllib.error.URLError,
                subprocess.CalledProcessError,
            ) as error:
                logger.debug(
                    "Retrieval method %s failed for %s",
                    kind,
                    resource["path"],
                    exc_info=True,
                )
                errors.append(f"{kind}: {type(error).__name__}")
        raise RuntimeError(
            f"Cannot prepare {resource['path']}: {'; '.join(errors) or 'no available source'}. "
            "Consult DATA.md or provide --archive-root."
        )
    finally:
        temporary.unlink(missing_ok=True)


def prepare_provider(provider: dict, project: Path) -> None:
    """Prepare inputs through an existing course dependency.

    :param provider: Provider kind and assignment-relative destination.
    :param project: Assignment directory.
    :raises ImportError: If the original course dependency is unavailable.
    :raises ValueError: If the provider is unknown or its path escapes the project.
    """
    target = contained(project, provider["path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if provider["kind"] == "mnist":
        from torchvision.datasets import MNIST

        MNIST(str(target), train=True, download=True)
        MNIST(str(target), train=False, download=True)
    elif provider["kind"] == "uci":
        import pickle

        from ucimlrepo import fetch_ucirepo

        if not target.exists():
            dataset = fetch_ucirepo(id=provider["dataset_id"])
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    pickle.dump(dataset, stream)
                    stream.flush()
                    os.replace(temporary, target)
                finally:
                    temporary.unlink(missing_ok=True)
    elif provider["kind"] == "pdb":
        import sys

        subprocess.run(
            [sys.executable, str(contained(project, provider["script"]))],
            cwd=project,
            check=True,
        )
    else:
        raise ValueError("Unknown data provider: " + provider["kind"])
    logger.info("Prepared %s inputs at %s", provider["kind"], provider["path"])


def main(project: Path) -> int:
    """Run an assignment-specific downloader.

    :param project: Directory containing data_sources.json.
    :returns: Zero on success, one when requested inputs remain unavailable.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-root", type=Path, default=os.environ.get("MIGRATION_ARCHIVE")
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List declared inputs without accessing the network.",
    )
    parser.add_argument(
        "--include-artifacts",
        action="store_true",
        help="Also restore archived models and generated outputs.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    manifest = json.loads((project / "data_sources.json").read_text())
    resources = [
        r
        for r in manifest["resources"]
        if args.include_artifacts or r.get("role") == "input"
    ]
    if args.list:
        for resource in resources:
            print(resource["path"], resource.get("availability", "declared"), sep="\t")
        for item in manifest.get("unresolved", []):
            print("UNRESOLVED", item, sep="\t")
        for provider in manifest.get("providers", []):
            print(provider["path"], provider["kind"], sep="\t")
        return 0
    failures = []
    for resource in resources:
        try:
            retrieve(
                resource,
                project,
                Path(args.archive_root) if args.archive_root else None,
            )
        except (RuntimeError, ValueError) as error:
            logger.error("Input preparation failed: %s", error, exc_info=True)
            failures.append(resource["path"])
    for provider in manifest.get("providers", []):
        try:
            prepare_provider(provider, project)
        except (
            ImportError,
            OSError,
            ValueError,
            RuntimeError,
            subprocess.CalledProcessError,
        ) as error:
            logger.error("Provider preparation failed: %s", error, exc_info=True)
            failures.append(provider["path"])
    for item in manifest.get("unresolved", []):
        logger.warning(
            "Additional input requires the documented preparation step: %s", item
        )
    return int(bool(failures or manifest.get("unresolved")))
