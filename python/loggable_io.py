import io
import sys
import contextlib


class Loggable:
    """Interface for classes that will be passed in LoggableIO"""

    def save_log(self, s: str) -> None:
        """
        Implement logic to save logs

        Args:
            s: Logged string
        """
        raise NotImplementedError


class LoggableIO(io.TextIOBase):
    """Loggable Stream, calls save_log of object passed when write is called.

    Attributes:
        loggable_object: Loggable instance to which logs will be associated to
        terminal: variable holding value of sys.stdout
        pass_through: Flag, when set will pass to stdout as well


    Examples:

        from contextlib import redirect_stdout
        
        
        class LoggableFile:
        
            def save_log(self, s: str) -> None
                with open('log.txt', 'a') as f:
                    f.write(f"{s}\n")

        loggable = LoggableFile()

        with redirect_stdout(LoggableIO(loggable)):
            print("hello world")

    """

    def __init__(self, loggable_object: Loggable, pass_through: bool = True) -> None:
        """Inits LoggableIO

        Args:
            loggable_object: Loggable instance to which logs will be associated to
            pass_through: Flag, when set will pass to stdout as well
        """
        self.terminal: io.TextIO = sys.stdout
        self.loggable_object = loggable_object
        self.pass_through = pass_through

    def write(self, s: str) -> int:
        """Write the string s to the stream

        Will call loggable_object.save_log(s), pass to stdout if set and also
        to the stream

        Args:
            String to write

        Returns:
            the number of characters written
        """
        with contextlib.redirect_stdout(self.terminal):
            # to avoid infinite recursion output of this is stdout
            self.loggable_object.save_log(s)

        if self.pass_through:
            return self.terminal.write(s)

        return len(s)
