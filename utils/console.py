import os


class ConsoleUtils:
    """
    A class that provides console utilities, such as clearing the console, setting the console title,
    clearing a file, and deleting a subset of files.

    Attributes:
        None

    Methods:
        clear_console():
            Clears the console.

        set_console_title(title: str):
            Sets the title of the console window.

        clear_file(file: str):
            Clears the contents of a given file.

        delete_files(confirm: bool):
            Deletes a subset of files that start with 'file' from the current directory.
    """

    @staticmethod
    def clear_console() -> None:
        """
        Clears the console window.

        Args:
            None

        Returns:
            None
        """
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            os.system('cls')
        elif os.name in ('linux', 'osx', 'posix'):
            os.system('clear')
        else:
            print('Your operating system is not supported.')

    @staticmethod
    def set_console_title(title: str) -> None:
        """
        Sets the title of the console window.

        Args:
            title: A string representing the title to set.

        Returns:
            None
        """
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            import ctypes

            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif os.name in ('linux', 'osx', 'posix'):
            os.system(f'echo -ne "\033]0;{title}\007"')
        else:
            print('Your operating system is not supported.')

    @staticmethod
    def clear_file(file: str) -> None:
        """
        Clears the contents of a given file.

        Args:
            file: A string representing the file to clear.

        Returns:
            None
        """
        with open(file, 'r+') as f:
            f.truncate(0)

    @staticmethod
    def delete_files(confirm: bool) -> None:
        """
        Deletes a subset of files that start with 'file' from the current directory.

        Args:
            confirm: A boolean indicating whether to ask for confirmation before deleting the files.

        Returns:
            None
        """
        for file in os.listdir():
            if file.startswith('file'):
                if confirm:
                    response = input(
                        f'Are you sure you want to delete {file}? (y/n) '
                    )
                    if response.lower() != 'y':
                        continue
                os.remove(file)
