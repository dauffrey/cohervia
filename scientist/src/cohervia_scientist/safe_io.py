"""POSIX bounded IO; deployments must keep holdouts unmounted and source read-only."""
from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path


def local_path(root: Path, relative: str) -> Path:
    root = Path(root).absolute()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or '..' in root.parts:
        raise ValueError('path must not contain traversal')
    path = root / rel
    for part in (*reversed(path.parents), path):
        if part.is_symlink():
            raise ValueError('symlink paths are prohibited')
    return path


@contextmanager
def directory_fd(path: Path):
    """Pin every directory component; reject symlinks even during a rename race."""
    if not hasattr(os, 'O_NOFOLLOW') or not hasattr(os, 'O_DIRECTORY'):
        raise RuntimeError('bounded reasoning IO requires POSIX no-follow directory access')
    path = Path(path).absolute()
    if '..' in path.parts:
        raise ValueError('directory traversal is prohibited')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read_local(root: Path, relative: str, *, max_bytes: int) -> bytes:
    path = local_path(root, relative)
    with directory_fd(path.parent) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError('input must be a regular file without hard links')
            data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f'input exceeds byte budget: {relative}')
    return data
