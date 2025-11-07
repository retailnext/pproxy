import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Union, Optional, Sequence

# Check that python hasn't been unexpectedly upgraded
#
# If python has been upgraded, we need to make sure it's in sync with the
# build step and the constraint in renovate.json
if sys.version_info.major != 3 or sys.version_info.minor != 11:
    sys.exit(sys.version_info)

# Check that pycrypto isn't broken
import cryptography.hazmat.backends.openssl.backend

if not cryptography.hazmat.backends.openssl.backend:
    sys.exit('cryptography is not okay')

# Check that pproxy can be started
subprocess.check_call(["/usr/local/bin/pproxy", "--version"])


class ChildProcess:
    """
    Context manager to run a child process while other code executes.

    Parameters:
    - args: sequence or string of args used to launch subprocess (same as subprocess.Popen args)
    - prefix: string to prepend to every line read from stdout and stderr
    - cwd: optional working directory for the child
    - env: optional environment mapping for the child

    Example:
        with ChildProcess(["python", "-u", "myscript.py"], prefix="[worker] "):
            do_other_work()
    """

    def __init__(
            self,
            args: Union[str, Sequence[str]],
            prefix: str = "",
            cwd: Optional[str] = None,
            env: Optional[dict] = None,
    ):
        self.args = args
        self.prefix = prefix
        self.cwd = cwd
        self.env = env

        self.proc: Optional[subprocess.Popen] = None
        self._threads: list[threading.Thread] = []

    def __enter__(self) -> "ChildProcess":
        # Start the subprocess with pipes for stdout and stderr.
        self.proc = subprocess.Popen(
            self.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=self.env,
            text=True,  # uses universal newlines; same as universal_newlines=True
            bufsize=1,  # line buffered
        )

        # Reader function for a given pipe -> writes to the appropriate std stream.
        def _reader(pipe, target_stream):
            try:
                # iter(pipe.readline, '') reads until EOF
                for line in iter(pipe.readline, ""):
                    if not line:
                        break
                    # Ensure each line is prefixed; line already contains newline if any.
                    try:
                        target_stream.write(f"{self.prefix}{line}")
                        target_stream.flush()
                    except Exception:
                        # Best-effort: if writing fails, stop reading
                        break
            finally:
                try:
                    pipe.close()
                except Exception:
                    pass

        # Start threads to forward stdout and stderr
        if self.proc.stdout is not None:
            t_out = threading.Thread(
                target=_reader, args=(self.proc.stdout, sys.stdout), name="child_stdout_reader"
            )
            t_out.daemon = False
            t_out.start()
            self._threads.append(t_out)

        if self.proc.stderr is not None:
            t_err = threading.Thread(
                target=_reader, args=(self.proc.stderr, sys.stderr), name="child_stderr_reader"
            )
            t_err.daemon = False
            t_err.start()
            self._threads.append(t_err)

        return self

    def terminate(self, wait_secs: float = 5.0) -> None:
        """
        Terminate the child process: send terminate(), wait up to wait_secs,
        and if still alive send kill().
        """
        if not self.proc:
            return

        if self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception:
                pass

            try:
                self.proc.wait(timeout=wait_secs)
            except subprocess.TimeoutExpired:
                # If it didn't die, force kill
                try:
                    self.proc.kill()
                except Exception:
                    pass
                try:
                    self.proc.wait(timeout=2)
                except Exception:
                    pass

    def __exit__(self, exc_type, exc, tb) -> None:
        # Terminate the child if still running.
        try:
            self.terminate()
        finally:
            # Wait for reader threads to finish reading remaining output.
            for t in self._threads:
                try:
                    t.join(timeout=2.0)
                except Exception:
                    pass

            # Close any remaining file descriptors on the process object.
            if self.proc:
                try:
                    if self.proc.stdout and not self.proc.stdout.closed:
                        self.proc.stdout.close()
                except Exception:
                    pass
                try:
                    if self.proc.stderr and not self.proc.stderr.closed:
                        self.proc.stderr.close()
                except Exception:
                    pass

        # Do not suppress exceptions from the with-block.
        return False


def fetch_via_http_proxy(
        url: str,
        proxy: str,
        timeout: int = 10,
        max_retry_time: float = 30.0,
        sleep_between_attempts: float = 0.1,
) -> None:
    """
    Fetch a URL through an HTTP proxy (used for both http and https).
    Retries on any error, waiting a fixed amount of time between attempts.

    Parameters:
    - url: target URL to fetch.
    - proxy: HTTP proxy URL (e.g. "http://proxy.host:3128"). Used for both http and https.
    - timeout: per-request timeout in seconds.
    - max_retry_time: overall retry budget in seconds.
    - sleep_between_attempts: fixed wait time between attempts in seconds (default 0.1).

    The function returns None and does not print anything when the GET succeeds.
    Raises RuntimeError when the retry budget is exhausted.
    """
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    )
    req = urllib.request.Request(url)

    start = time.monotonic()
    attempt = 0

    while True:
        attempt += 1
        try:
            with opener.open(req, timeout=timeout) as resp:
                # successful fetch: do not print anything, just return
                resp.read(1)
                return
        except Exception as err:
            elapsed = time.monotonic() - start
            if elapsed >= max_retry_time:
                raise RuntimeError(f"Giving up after {elapsed:.1f}s while fetching {url}") from err

            sleep_time = min(sleep_between_attempts, max_retry_time - elapsed)
            print(f"Attempt {attempt} failed ({err}); retrying in {sleep_time:.2f}s (elapsed {elapsed:.2f}s)...")
            time.sleep(sleep_time)


# Check that pproxy can be used as an http proxy to access http and https servers
with ChildProcess(["/usr/local/bin/pproxy", "-l", "http://:8080", "-v"], "pproxy:"):
    with ChildProcess(["/usr/local/bin/python", "-m", "http.server", "8081"], "http.server:"):
        fetch_via_http_proxy("http://localhost:8081/", "http://localhost:8080")
        fetch_via_http_proxy("https://github.com/robots.txt", "http://localhost:8080")
