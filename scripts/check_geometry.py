"""Compatibility entry point for the complete workbook review."""

if __package__:
    from .review import main
else:
    from review import main


if __name__ == "__main__":
    raise SystemExit(main())
