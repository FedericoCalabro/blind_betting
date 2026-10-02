import contextlib
import re
import subprocess
import sys
import time
from threading import Event, Lock, Thread
from typing import Protocol

ITALIAN = re.compile(r"(.+?)\s+it_IT\b")


class Speaker(Protocol):
    def start(self) -> None: ...
    def say(self, text: str) -> None: ...
    def wait(self, timeout: float = 15) -> None: ...
    def close(self) -> None: ...


def speaker(rate: int) -> Speaker:
    return MacSpeaker(rate) if sys.platform == "darwin" else EngineSpeaker(rate)


class EngineSpeaker(Thread):
    def __init__(self, rate: int):
        super().__init__(daemon=True)
        self.rate = rate
        self._lock = Lock()
        self._pending: str | None = None
        self._busy = Event()
        self._closed = Event()

    def say(self, text: str) -> None:
        with self._lock:
            self._pending = text
            self._busy.set()

    def wait(self, timeout: float = 15) -> None:
        deadline = time.monotonic() + timeout
        while self._busy.is_set() and time.monotonic() < deadline:
            time.sleep(0.1)

    def close(self) -> None:
        self._closed.set()
        self.join(timeout=2)

    def run(self) -> None:
        import pyttsx3

        # SAPI5 is COM: the engine must only be touched by the thread that created it.
        engine = pyttsx3.init()
        engine.setProperty("rate", self.rate)
        for voice in engine.getProperty("voices"):
            if "it-it" in str(voice.id).lower().replace("_", "-"):
                engine.setProperty("voice", voice.id)
                break
        engine.startLoop(False)
        while not self._closed.is_set():
            with self._lock:
                text, self._pending = self._pending, None
            if text is not None:
                engine.stop()
                engine.say(text)
            else:
                engine.iterate()
                if not engine.isBusy():
                    with self._lock:
                        if self._pending is None:
                            self._busy.clear()
            time.sleep(0.05)
        engine.endLoop()


class MacSpeaker:
    # pyttsx3's macOS driver never reports the end of an utterance outside the main thread's
    # run loop, so on a Mac each sentence is a `say` process, killed by the next one.
    def __init__(self, rate: int):
        self.rate = rate
        self._lock = Lock()
        self._process: subprocess.Popen | None = None
        voices = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
        italian = [found[1] for line in voices.splitlines() if (found := ITALIAN.match(line))]
        self._voice = ["-v", italian[0]] if italian else []

    def start(self) -> None:
        pass

    def say(self, text: str) -> None:
        with self._lock:
            self._stop()
            self._process = subprocess.Popen(["say", "-r", str(self.rate), *self._voice, text])

    def wait(self, timeout: float = 15) -> None:
        if self._process is not None:
            with contextlib.suppress(subprocess.TimeoutExpired):
                self._process.wait(timeout)

    def close(self) -> None:
        with self._lock:
            self._stop()

    def _stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
