"""Wrappers around standard library multiprocessing executors."""
import concurrent.futures
import multiprocessing
import threading

try:
    from multiprocessing.queues import Queue as _mpQueue
except AttributeError:
    from multiprocessing import Queue as _mpQueue


class _Executor(object):

    def submit(self, fn, *args, **kwargs):
        self.semaphore.acquire()
        future = super().submit(fn, *args, **kwargs)
        future.add_done_callback(self._release)

        return future

    def _release(self, future):
        self.semaphore.release()


class ProcessPoolExecutor(_Executor, concurrent.futures.ProcessPoolExecutor):
    """Extends `ProcessPoolExecutor` by limiting simultaneous work items."""

    def __init__(self, max_items, **kwargs):
        """Initialize a process pool.

        :param max_items: maximum number of simultaneous work items.
            Calls to `.submit` will block if there are too many unprocessed
            items.
        :param kwargs: key-word arguments to `ProcessPoolExecutor`.
        """
        super().__init__(**kwargs)
        self.semaphore = multiprocessing.BoundedSemaphore(max_items)


class ThreadPoolExecutor(_Executor, concurrent.futures.ThreadPoolExecutor):
    """Extends `ThreadPoolExecutor` by limiting simultaneous work items."""

    def __init__(self, max_items, **kwargs):
        """Initialize a thread pool.

        :param max_items: maximum number of simultaneous work items.
            Calls to `.submit` will block if there are too many unprocessed
            items.
        :param kwargs: key-word arguments to `ThreadPoolExecutor`.
        """
        super().__init__(**kwargs)
        self.semaphore = threading.BoundedSemaphore(max_items)


class Counter:
    """A shared counter object with safe increment/decrement."""

    def __init__(self, initial=0):
        """Initialise the counter."""
        self._count = multiprocessing.Value('i', initial)

    @property
    def value(self):
        """Return the current value of the counter."""
        return self._count.value

    def increment(self, amount=1):
        """Increment the counter."""
        with self._count.get_lock():
            self._count.value += amount
        return self

    def decrement(self, amount=1):
        """Decrement the counter."""
        with self._count.get_lock():
            self._count.value -= amount


class Queue(_mpQueue):
    """A `multiprocessing.Queue` that keeps track of its size.

    The class reimplements `.qsize()` in a way that works on macOS.
    """

    def __init__(self, **kwargs):
        """Initialize the class."""
        super().__init__(
            ctx=multiprocessing.get_context(), **kwargs)
        self._size = Counter(0)

    def put(self, *args, **kwargs):
        """Put an object in the Queue."""
        super().put(*args, **kwargs)
        self._size.increment()

    def get(self, *args, **kwargs):
        """Get an object from the Queue."""
        rval = super().get(*args, **kwargs)
        self._size.decrement()
        return rval

    def qsize(self):
        """Return the size of the queue."""
        return self._size.value

    def empty(self):
        """Return if the queue is empty."""
        return self.qsize() == 0
