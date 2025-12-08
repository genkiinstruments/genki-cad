from multiprocessing.synchronize import Event as EventClass
from ocp_vscode.__main__ import main as ocp_main
from importlib import import_module
from argparse import ArgumentParser
import multiprocessing as mp
from types import ModuleType
from typing import Callable
import webbrowser
import watchfiles
import enum
import sys
import os


WATCH_MODULE = "watch"


class Message(enum.Enum):
    UPDATE = 1
    CLOSE = 2


def watch(
    mod: ModuleType,
    predicate: Callable[[str], bool],
    reload_event: EventClass,
    queue: "mp.Queue[Message]",
) -> None:
    try:
        if not mod.__file__:
            raise AttributeError(f"{mod} missing __file__")

        for changes in watchfiles.watch(mod.__file__, "."):
            match = False
            for change in changes:
                path = os.path.abspath(change[1])

                if path == mod.__file__:
                    reload_event.set()
                    break

                if predicate(path):
                    match = True
            else:
                if match:
                    queue.put(Message.UPDATE)
                continue
            break
    finally:
        queue.put(Message.CLOSE)
        queue.close()


def spawn(run: Callable[[], None], queue: "mp.Queue[Message]") -> None:
    """
    Will run mod.run() for every change.
    """
    while True:
        msg = queue.get()
        match msg:
            case Message.UPDATE:
                pid = os.fork()
                if pid == 0:
                    run()
                    break
                os.waitpid(pid, 0)
            case Message.CLOSE:
                break


def main_loop(reload_event: EventClass) -> None:
    mod = import_module(WATCH_MODULE)

    # Assign a default predicate matching Python files unless one is provided by the module.
    predicate: Callable[[str], bool]
    try:
        predicate = getattr(mod, "predicate")
        if not callable(predicate):
            raise ValueError("Predicate function not callable")
    except AttributeError:
        def py_predicate(path: str) -> bool:
            return path.endswith(".py")
        predicate = py_predicate

    # Function to call on change
    run: Callable[[], None] = getattr(mod, "run")

    # Queue to send update events from file watcher to fork server
    queue: "mp.Queue[Message]" = mp.Queue()

    # File watcher process
    watch_p = mp.Process(
        target=watch,
        args=(
            mod,
            predicate,
            reload_event,
            queue,
        ),
    )
    watch_p.start()

    # Child spawner process
    spawn_p = mp.Process(
        target=spawn,
        args=(
            run,
            queue,
        ),
    )
    spawn_p.start()

    # Initial render after reload
    queue.put(Message.UPDATE)

    # Wait for processes to exit
    watch_p.join()
    spawn_p.join()


def main() -> None:
    # Use fork on macOS to avoid pickling issues with Click commands
    mp.set_start_method("fork")

    # Hand off help to standalone ocp viewer
    if "--help" in sys.argv or "-h" in sys.argv:
        ocp_main()
        exit()

    # Get port option definition from standalone viewer
    port_opts = [option for option in ocp_main.params if option.name == "port"]
    if len(port_opts) != 1:
        raise ValueError("More than one port option found")
    port_opt = port_opts[0]

    # Construct an argument parser to get the port
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--port", default=port_opt.default, type=int)

    # Extract port argument, add to env
    args = arg_parser.parse_known_args()[0]
    os.environ["OCP_PORT"] = str(args.port)

    # Make working directory modules importable
    sys.path.append(".")

    ocp_p = mp.Process(target=ocp_main)
    ocp_p.start()

    # Open browser after a short delay to let server start
    webbrowser.open(f"http://127.0.0.1:{args.port}")

    # Event to keep track of whether to exit
    reload_event = mp.Event()

    # Run watcher loop
    while True:
        watch_p = mp.Process(target=main_loop, args=(reload_event,))
        watch_p.start()

        # Check if we should exit or reload
        watch_p.join()
        if not reload_event.is_set():
            break
        reload_event.clear()

    ocp_p.kill()
    ocp_p.join()
