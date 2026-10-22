from argparse import ArgumentParser

from .error import Error, TypedVariant, Variant

__all__ = ["Error", "TypedVariant", "Variant"]


def main(args: list[str] | None = None) -> None:
    """Show package usage for the installed console-script entry point."""
    parser = ArgumentParser(prog="thiserror", description="A declarative error library for Python.")
    parser.parse_args(args)
    parser.print_help()
