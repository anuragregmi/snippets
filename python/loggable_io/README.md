# Loggable IO

IO class when used will stream to `stdout` and also performs `save`

## Example
The example below will redirect print statement to a file and will also print
on stdout
```py3
from contextlib import redirect_stdout

class LoggableFile:
    """
    Log to a file
    """

    def __init__(self, filename) -> None:
        self.filename = filename

    def save_log(self, s: str) -> None:
        with open(self.filename, 'a') as f:
            f.write(f"{s}")

loggable = LoggableFile("log.txt")

with redirect_stdout(LoggableIO(loggable)):
    print("hello world")
```