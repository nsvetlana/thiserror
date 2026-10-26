#!/usr/bin/env python3
import subprocess
import sys


def main() -> None:
    args_str = " ".join(sys.argv[1:])

    subprocess.run(f"uv version --bump {args_str}", shell=True, check=True)

    version = subprocess.run(
        "uv version --short",
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    git_chain = (
        "git add pyproject.toml uv.lock && "
        f'git commit -m "{version}" && '
        f'git tag "v{version}"'
    )
    subprocess.run(git_chain, shell=True, check=True)


if __name__ == "__main__":
    main()
