import shutil
from os import path
from tempfile import NamedTemporaryFile
from typing import List

from lib.constants import LATIN_1_ENCODING
from lib.logger import LOGGER
from lib.shell_command import ShellCommand
from lib.variant import Variant


class DicChunk:
    """This class represents a single chunk of a Hunspell dictionary file.

    Attributes:
        filepath (str): the path to the chunk
        name (str): the name of the chunk (e.g. chunk0)
        compounds (bool): whether this is a file containing compounds or not; if True, this chunk will *not* be
                          tokenised;
    """
    def __init__(self, filepath: str, name: str, compounds: bool = False):
        self.filepath = filepath
        self.name = name
        self.compounds = compounds

    def __str__(self) -> str:
        basename = path.basename(self.filepath)
        if self.compounds:
            return path.join('compounds', basename)
        return basename

    def rm(self) -> None:
        """Remove the chunk file."""
        LOGGER.debug(f"Removing {self} ...")
        shutil.rmtree(self.filepath)

    @classmethod
    def from_hunspell_dic(cls, variant: Variant, chunk_size: int, target_dir: str, sample_size: int,
                          compounds: bool = False) -> List:
        """Splits a dictionary file into smaller files (chunks) of a given number of lines.

        Args:
            variant (Variant): the variant for which we want to unmunch the .dic file
            chunk_size (int): the number of lines per chunk
            target_dir (str): the directory where the chunks will be saved
            sample_size (int): the number of lines to read from the dictionary file; if 0 or negative, read all lines
            compounds (bool): whether this is a file containing compounds or not

        Returns:
            A list of DicChunk objects, each representing a chunk of the dictionary file
        """
        if compounds:
            tmp_dir = path.join(target_dir, 'compounds')
            dic_path = variant.compounds()
        else:
            tmp_dir = target_dir
            dic_path = variant.dic()
        LOGGER.debug(f"Splitting dictionary file \"{dic_path}\" into chunks...")
        with open(dic_path, 'r', encoding=LATIN_1_ENCODING) as dic_file:
            lines = dic_file.readlines()[1:]  # Skip the first line
        lines = [line for line in lines if not line.startswith("#")]  # Filter out comment lines
        if sample_size > 0:
            lines = lines[0:sample_size]
        total_lines = len(lines)
        str_chunks: List[List[str]] = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
        chunks: List[cls] = []
        for index, chunk in enumerate(str_chunks):
            chunk_name = f"{variant.underscored}_chunk{index}"
            filename = chunk_name + ".dic"
            chunk_path = path.join(tmp_dir, filename)
            with open(chunk_path, 'w', encoding=LATIN_1_ENCODING) as chunk_file:
                # Prepend the count of lines in this chunk and then write all lines
                chunk_file.write(f"{len(chunk)}\n")
                chunk_file.writelines(chunk)
            chunks.append(cls(chunk_path, chunk_name, compounds))
        LOGGER.debug(f"Split into {len(chunks)} chunks.")
        return chunks

    def unmunch(self, aff_path: str, delete_tmp: bool = False) -> NamedTemporaryFile:
        """Create all forms from Hunspell dictionaries.

        Args:
            aff_path: the path to the .aff file
            delete_tmp: whether to delete the temporary file after use

        Returns:
            the temp file containing the unmunched dictionary
        """
        unmunched_tmp = NamedTemporaryFile(delete=delete_tmp, mode='wb',
                                           prefix=f"{self.name}_unmunched_")
        LOGGER.debug(f"Unmunching {self} into {unmunched_tmp.name} ...")
        cmd_unmunch = f"unmunch {self.filepath} {aff_path}"
        unmunch_result = ShellCommand(cmd_unmunch).run()
        unmunched_tmp.write(unmunch_result)
        unmunched_tmp.flush()
        if delete_tmp:
            self.rm()
        return unmunched_tmp
