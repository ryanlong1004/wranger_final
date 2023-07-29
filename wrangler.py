#!/usr/bin/env python3
"""main execution"""

import argparse
import glob
import itertools
import json
import logging
import os
import pathlib
import re
from pathlib import Path
from typing import Any, Generator

import yaml

logger = logging.getLogger(__name__)


class CLI:
    """represents the users response to a CLI input"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="wrangler",
            description="Parses and transcribes yaml files to lua scripts",
            epilog="Example: wrangler --output-path ./temp file.yaml path",
        )

        self.parser.add_argument("paths", nargs="*", type=pathlib.Path)
        self.parser.add_argument("--output-path", type=pathlib.Path, required=True)

    def get_user_input(self) -> dict[str, Any]:
        """queries the user and returs their input"""
        args = self.parser.parse_args()
        self.validate_output_path(args.output_path)
        return {"output_path": args.output_path, "queue": self.get_queue(args.paths)}

    @staticmethod
    def validate_output_path(output_path):
        """validates the output_path is not None and exists"""
        if not Path(output_path).exists():
            logger.warning("'%s' directory does not exist... creating", output_path)
            output_path.mkdir(parents=True, exist_ok=True)

    def get_queue(self, _paths: list[pathlib.Path]) -> Generator[Path, None, None]:
        """creates generator of files for parsing"""
        for _path in _paths:
            # NOTE: This is a little dangerous
            # NOTE: What if the directory contains yamls not of the type this program can transcribe?
            # NOTE: instead, ask the user a specific yaml or validate the yaml matches
            # NOTE: help, whatis, content keys?
            if _path.is_dir():
                for _file in glob.glob(f"{_path.absolute()}/*yaml", recursive=True):
                    yield Path(_file)
            else:
                yield _path


class LuaTranslator:
    """Translates key, value pairs to Lua commands"""

    _ENV_RE = re.compile(r"\$[{]?(?P<envkey>[a-zA-Z0-9_]*)[}]?")

    def __init__(self):
        pass

    def __call__(self, key, value):
        """executes the function on value returned by key lookup

        Allows use of any translator that follows this interface
        """
        _map = {
            "modules": self.modules,
            "modulepaths": self.modulepaths,
            "environment": self.environment,
            "help": self.help,
            "whatis": self.whatis,
        }
        return _map.get(key, lambda x: x)(value)

    @staticmethod
    def ensure_list(value):
        """ensures a value is a list or coerces to list of len 1"""
        return value if isinstance(value, list) else [value]

    def modulepaths(self, values: list[str]) -> list[str]:
        """returns lua module path commands"""
        if not values:
            return []
        return [
            f'prepend_path("MODULEPATH", pathJoin("{_path}"))\n'
            for _path in self.ensure_list(values)
            if _path != "None"
        ]

    def modules(self, values: list[str]) -> list[str]:
        """returns list of lua module commands

        Environment variables are translated if they exist in the
        environtment.  Otherwise, returns the environment lookup as
        a Lua command.
        """
        results = []
        if not values:
            return results
        for value in self.ensure_list(values):
            try:
                key, _value = value.split("/")
                env_value = self.get_environment_value(_value)
                results.append(f'load(pathJoin("{key}", {env_value}))\n')
            except ValueError:
                results.append(f'load("{value}")\n')
        return results

    def environment(self, values: list[dict[str, Any]]) -> list[str]:
        """returns list of lua environment variable commands"""

        results = []
        if not values:
            return results
        for value in self.ensure_list(values):
            for key, value in value.items():
                results.append(f'setenv("{key}", "{value}")\n')
        return results

    @classmethod
    def get_environment_value(cls, key) -> str:
        """returns the os environment value if it exists or a lua environment lookup otherwise"""
        mm = cls._ENV_RE.match(key)
        if mm:
            envkey = mm.group("envkey")
            if envkey is not None:
                value = os.getenv(envkey)
                if value is None:
                    value = f'os.getenv("{envkey}")'
            return value
        else:
            return f'"{key}"'

    def whatis(self, values: list[str]) -> list[str]:
        """returns list Lua whatis commands"""
        if not values:
            return []
        return [f'whatis("{value}")\n' for value in self.ensure_list(values)]

    def help(self, values: list[str]) -> list[str]:
        """returns list of Lua help commands"""
        if not values:
            return []
        return [f"help([[{value}]])\n" for value in self.ensure_list(values)]


class Script:
    """represents a Script whose data is to be parsed and translated"""

    def __init__(self, name, data, translator):
        self.name = name
        self.data = data
        self.translator = translator

    def __str__(self):
        return str(list(itertools.chain(self.help, self.content, self.whatis)))

    def __repr__(self):
        props = self.__dict__.copy()
        props.pop("translator")
        return json.dumps(props)

    @property
    def content(self):
        """returns the content translated by translator or an empty list"""
        value = self.data.get("content", [])
        return list(
            itertools.chain(
                *[
                    self.translator(key, content)
                    for item in value
                    for key, content in item.items()
                ]
            )
        )

    @property
    def help(self):
        """returns the help translated by translator or None"""
        return self.translator("help", self.data.get("help", None))

    @property
    def whatis(self):
        """returns the whatis translated by translator or None"""
        return self.translator("whatis", self.data.get("whatis", None))


def queue(_files):
    """parses _files into Script instances"""
    for _file in _files:
        logging.debug("queueing %s", _file)
        with open(_file, "r", encoding="utf-8") as _file:
            translator = LuaTranslator()
            yield [
                Script(script_name, data, translator)
                for (script_name, data) in yaml.safe_load(_file).items()
                if "^" not in script_name
            ]


def write_scripts_to_files(scripts: list[Script], output_path: Path):
    """writes a list of Script instances to files at output path"""
    for script in scripts:
        with open(
            Path(output_path / f"{script.name}.lua"), "w", encoding="utf-8"
        ) as _file:
            logger.debug("writing %s", _file.name)
            _file.writelines(
                itertools.chain(script.help, script.content, script.whatis)
            )


def main():
    """main execution"""

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.setLevel(logging.DEBUG)

    data = CLI().get_user_input()
    inputs: Generator[Path, None, None] = data["queue"]
    output_path: Path = data["output_path"]

    for scripts in queue(inputs):
        write_scripts_to_files(scripts, output_path)


if __name__ == "__main__":
    main()
