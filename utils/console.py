import os
import platform


class ConsoleUtils:
    """
    A class containing static methods for clearing the console, setting the console title,
    clearing a file, and purging a directory.
    """

    @staticmethod
    def clear_console() -> None:
        """
        Clears the console window.

        Returns:
            None
        """
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def set_console_title(title: str) -> None:
        """
        Sets the title of the console window.

        Args:
            title: A string representing the title to set.

        Returns:
            None
        """
        if platform.system() == 'Windows':
            import ctypes

            ctypes.windll.kernel32.SetConsoleTitleW(title)
        else:
            os.system(f'echo -ne "\033]0;{title}\007"')

    @staticmethod
    def clear_file(file_path: str) -> None:
        """
        Clears the contents of a given file.

        Args:
            file_path: A string representing the path of the file to clear.

        Returns:
            None
        """
        with open(file_path, 'w') as f:
            f.truncate(0)

    @staticmethod
    def purge_directory(directory: str) -> None:
        """
        Deletes all files in a given directory.

        Args:
            directory: A string representing the path of the directory to purge.

        Returns:
            None
        """
        for file in os.listdir(directory):
            try:
                os.remove(os.path.join(directory, file))
            except OSError:
                print(f'Failed to delete {file}.')
