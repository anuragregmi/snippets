import json
import asyncio
from django.conf import settings


async def send_data(data: str):
    """Send data to unix connection to background task server

    Args:
        data: json dumped task detail
    """
    print("SCHEDULING")

    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    reader, writer = await asyncio.open_unix_connection(settings.SOCKET_PATH)

    writer.write(data.encode())

    data = await reader.read(600)

    writer.close()

    print("RECEIVED", data)


async def async_run_in_background(fn_path: str, *args, **kwargs) -> None:
    """Async version of run_in_background
    
    Args:
        fn_path: path of function to be called eg. tasks.utils.send_data
        *args: arguments to be passed into that function (must be json serializable)
        **kwargs: keywork arguments to be passed into that function (must be json serializable)
    """
    data: str = json.dumps({'name': fn_path, 'args': args, 'kwargs': kwargs})
    await send_data(data)


def run_in_background(fn_path: str, *args, **kwargs) -> None:
    """Schedule a function call for background processing

    Args:
        fn_path: path of function to be called eg. tasks.utils.send_data
        *args: arguments to be passed into that function (must be json serializable)
        **kwargs: keywork arguments to be passed into that function (must be json serializable)

    """
    asyncio.run(async_run_in_background(fn_path, *args, **kwargs))
