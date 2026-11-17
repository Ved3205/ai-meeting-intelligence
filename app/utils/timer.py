"""
Execution time utilities.
"""

from time import perf_counter


class Timer:
    """
    Context manager for measuring execution time.
    Example:
    with Timer("Embedding"):
        create_embeddings()
    """

    def __init__(self, name: str = "Task"):
        self.name = name

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = perf_counter() - self.start
        print(f"{self.name} completed in {elapsed:.2f} seconds.")