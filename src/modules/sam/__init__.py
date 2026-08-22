"""SAM (Segment Anything Model) integration via Ray Serve."""

# Lazy import SAMDeployment only when explicitly needed
# to avoid startup issues on HEAD node without segment_anything

__all__ = ["SAMDeployment"]

def __getattr__(name: str):
    """Lazy load SAMDeployment on first access."""
    if name == "SAMDeployment":
        from .deployment import SAMDeployment
        return SAMDeployment
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
