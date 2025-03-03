import multiprocessing
import time
import queue
import signal
from rich import print


class ProcessManager:
    def __init__(self, num_processes=3):
        self.num_processes = num_processes
        self.processes = []
        self.task_queue = multiprocessing.Queue()
        self.results_queue = multiprocessing.Queue()
        self.stop_event = multiprocessing.Event()
        # Add a flag to track if we're still discovering pages
        self.discovering_pages = True
        self.processed_count = 0
        self.pages_count = 0

    def start(self, start_url, process_function, total_pages=None):

        # First, fill the task queue with initial URLs or page numbers
        if total_pages:
            # If we know total pages, distribute them
            for page_num in range(1, total_pages + 1):
                page_url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
                self.task_queue.put(page_url)
                self.pages_count += 1
            self.discovering_pages = False  # We know all pages upfront
        else:
            # We'll discover pages as we go, start with the first one
            self.task_queue.put(start_url)
            self.pages_count = 1

        print(f"Starting with {self.pages_count} page(s) in queue")

        # Store the worker function
        self._worker_function = process_function

        # Start worker processes
        for i in range(self.num_processes):
            p = multiprocessing.Process(
                target=self._worker_function,
                args=(i, self.task_queue, self.results_queue, self.stop_event),
            )
            p.daemon = True  # Process will exit when main process exits
            self.processes.append(p)
            p.start()
            print(f"Started process {i} with PID {p.pid}")

        # Monitor processes and handle results
        self._monitor_processes()

    def _monitor_processes(self):

        idle_count = 0
        max_idle_checks = 15  # Increased for more patience
        last_processed_count = 0
        last_pages_count = 0

        try:
            # Give processes time to start up
            time.sleep(3)

            while (
                any(p.is_alive() for p in self.processes)
                and not self.stop_event.is_set()
            ):
                # Check if any process has died
                for i, process in enumerate(self.processes):
                    if not process.is_alive():
                        print(f"Process {i} (PID: {process.pid}) died. Restarting...")
                        # Start a new process to replace the dead one
                        new_process = multiprocessing.Process(
                            target=self._worker_function,
                            args=(
                                i,
                                self.task_queue,
                                self.results_queue,
                                self.stop_event,
                            ),
                        )
                        new_process.daemon = True
                        new_process.start()
                        print(f"Restarted process {i} with new PID {new_process.pid}")
                        self.processes[i] = new_process

                # Process results
                results_processed = False
                try:
                    # Process all available results
                    while True:
                        result = self.results_queue.get(timeout=0.1)
                        results_processed = True

                        if result == "FOUND_NEW_PAGE":
                            # A process found a new page to process
                            new_url = self.results_queue.get()
                            print(f"Adding new page to queue: {new_url}")
                            self.task_queue.put(new_url)
                            self.discovering_pages = True  # We're still finding pages
                            self.pages_count += 1
                            print(
                                f"Added new page to queue: {new_url} (Total pages found: {self.pages_count})"
                            )

                        elif result == "COMPLETED_TASK":
                            # A process completed a task
                            print(
                                f"Completed a task. Queue size approximately: {self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 'unknown'}"
                            )

                        elif result == "BOOK_DATA":
                            # Process scraped a book
                            book_data = self.results_queue.get()
                            self.processed_count += 1
                            # Call the provided callback to handle the book data
                            if self._process_book_data:
                                self._process_book_data(book_data)
                            print(f"Processed {self.processed_count} books so far")

                except queue.Empty:
                    # No more results for now
                    pass

                # Check if there's been progress
                if (
                    self.processed_count > last_processed_count
                    or self.pages_count > last_pages_count
                ):
                    # Progress has been made, reset idle counter
                    idle_count = 0
                    last_processed_count = self.processed_count
                    last_pages_count = self.pages_count

                # Check queue status - IMPROVED THIS SECTION
                try:
                    is_queue_empty = self.task_queue.empty()
                except (NotImplementedError, AttributeError):
                    # Some platforms don't implement queue.empty()
                    # Try with qsize first
                    try:
                        is_queue_empty = self.task_queue.qsize() == 0
                    except (NotImplementedError, AttributeError):
                        # Fall back to try/except with a get
                        try:
                            # Try with a very small timeout
                            item = self.task_queue.get(block=True, timeout=0.01)
                            # Put it back
                            self.task_queue.put(item)
                            is_queue_empty = False
                        except queue.Empty:
                            is_queue_empty = True

                # Check if we should stop
                if is_queue_empty:
                    if results_processed:
                        # Results were processed this loop, reset idle counter
                        idle_count = 0
                    else:
                        # No results and queue is empty, increment idle counter
                        idle_count += 1
                        print(
                            f"System idle check {idle_count}/{max_idle_checks} (Discovered {self.pages_count} pages, Processed {self.processed_count} books)"
                        )

                    if idle_count >= max_idle_checks:
                        # We've been idle for too long
                        if self.pages_count < 50:  # We expect 50 pages
                            print(
                                f"WARNING: Only found {self.pages_count} pages but expected 50. Continuing..."
                            )
                            idle_count = (
                                max_idle_checks // 2
                            )  # Reset partially to give more time
                        else:
                            self.stop_event.set()
                            print(
                                f"All tasks completed. Processed {self.processed_count} books across {self.pages_count} pages. Stopping processes..."
                            )
                else:
                    # Queue has items, reset idle counter
                    idle_count = 0

                # Sleep a bit to avoid high CPU usage
                time.sleep(1)

        except KeyboardInterrupt:
            print("Received keyboard interrupt. Stopping all processes...")
            self.stop_event.set()
        finally:
            print("Waiting for processes to finish...")
            # Tell them to stop
            self.stop_event.set()

            # Wait for processes to exit
            for p in self.processes:
                p.join(timeout=5)

            # Force terminate any remaining processes
            for p in self.processes:
                if p.is_alive():
                    print(f"Terminating process {p.pid}")
                    p.terminate()

            print(
                f"Final results: Processed {self.processed_count} books across {self.pages_count} pages"
            )

    # Method that will be assigned by the main script
    _worker_function = None
    _process_book_data = None

    def set_worker_function(self, func):
        self._worker_function = func

    def set_book_data_handler(self, func):
        self._process_book_data = func
