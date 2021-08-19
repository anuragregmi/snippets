import asyncio
import json
import importlib
import traceback

from asgiref.sync import sync_to_async
from typing import Callable, Union
from types import ModuleType
from django.core.management.base import BaseCommand
from django.conf import settings


async def process_task(detail: dict) -> None:
    """Run task with details provided

    Args:
        detail: dictionary containing taks details
            if your function is defined as

                async def fn_name(first: str, second: str) 
            
            Then detail should be like

                {
                    "name": "module_name.fn_name",
                    "args": ["hello"],
                    "kwargs": { "second": "world" }
                }

            Values of "args" and "kwargs will be unpacked while calling fn
    """
    name: str = detail.get('name')
    args: Union(list, tuple) = detail.get('args')
    kwargs: dict = detail.get('kwargs')

    print(f'Processing task {name}')

    module_name: str
    attr: str
    module_name, attr = name.rsplit('.', maxsplit=1)
    module: ModuleType = importlib.import_module(module_name)
    fn: Callable = getattr(module, attr)

    if not asyncio.iscoroutinefunction(fn):
        fn = sync_to_async(fn, thread_sensitive=True)

    await fn(*args, **kwargs)

    print(f'Processed task {name}')


async def worker(name: str, queue: asyncio.Queue) -> None:
    """Waits for task to be available in queue, then process it

    Args:
        name: Name of worker
        queue: shared Queue instance to look for tasks
    """
    print(f"{name} listening")
    while True:
        # Get a "work item" out of the queue.
        task_body: dict = await queue.get()

        if task_body:
            try:
                await process_task(task_body)
            except Exception:
                traceback.print_exc()

            # Notify the queue that the "work item" has been processed.
            queue.task_done()


async def run_workers(queue: asyncio.Queue, number_workers: int = 4) -> None:
    """Run given number of workers together
    
    Args:
        queue: Shared Queue isinstance
        number_workers: Number of workers
    """
    tasks: list[asyncio.Task] = []
    for i in range(number_workers):
        task: asyncio.Task = asyncio.create_task(worker(f"Worker[{i}]", queue))
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)


def get_app(queue: asyncio.Queue) -> Callable:
    """Returns app (a callback function called when registering tasks)

    This factory function was needed because we could not pass extra arguments to
    the callback function.
    
    Args:
        queue: reference to asyncui.Queue where incoming tasks will be placed

    """

    async def app(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Callback function called when registering tasks

        This function will be passed as first parameter to `asyncio.create_unix_server`.

        Args:
            reader: StreamReader to read incoming stream
            writer: StreamWriter to write output
        """
        body: bytes = await reader.read(600)
        response: str = body.decode()
        task_details: dict = None
        try:
            request_json: dict = json.loads(response)
            name: str = request_json.get('name')
            if not name:
                raise ValueError
            args: Union(tuple, list) = request_json.get('args', tuple())
            if not isinstance(args, (list, tuple)):
                raise ValueError
            kwargs: dict = request_json.get('kwargs', dict())
            if not isinstance(kwargs, dict):
                raise ValueError
            task_details = {'name': name, 'args': args, 'kwargs': kwargs}

        except (json.JSONDecodeError, ValueError):
            writer.write("ERROR")

        if task_details:
            await queue.put(task_details)
            print("ENQUEUED", task_details["name"])
            writer.write(b"Queued")
        await writer.drain()

        writer.close()
    return app


async def run_q_server(queue: asyncio.Queue) -> None:
    """Run q_server to listen for incoming background tasks

    Args:
        queue: Shared Queue instance
    """
    print("Listening incoming queues from ", settings.SOCKET_PATH)
    server: asyncio.AbstractServer = await asyncio.start_unix_server(
        get_app(queue), settings.SOCKET_PATH
    )
    async with server:
        await server.serve_forever()


async def run_everything() -> None:
    """Run both q_server and workers togetger"""
    queue: asyncio.Queue = asyncio.Queue()

    server_task: asyncio.Task = asyncio.create_task(run_q_server(queue))
    worker_task: asyncio.Task = asyncio.create_task(run_workers(queue))

    await asyncio.gather(server_task, worker_task)

    await queue.join()


class Command(BaseCommand):

    help = 'Schedule and run background tasks'

    def handle(self, *args, **options) -> None:
        asyncio.run(run_everything())
        print("Closing")
