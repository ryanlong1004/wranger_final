# Wrangler

## Installation
Wrangler requires the PyYaml library.

`pip install pyyaml`

## Usage
```
usage: wrangler [-h] [--output-path PATH] [paths ...]

Parses and transcribes yaml files to lua scripts

positional arguments:
  paths

options:
  -h, --help            show this help message and exit
  --output-path OUTPUT_PATH

Example: wrangler --output-path file.yaml file2.yaml
```

Wrangler requires an output path to be specified with the flag `--output-path`.  This path can be relative or absolute and will be created if it does not already exist.

## Developer Notes

### Translators

The class `LuaTranslator` is an abstraction that keeps the parsing of the yaml files and the conversion to Lua separate.

It is passed to `Script` on instantiation in order to provide translation from
input (`yaml`) to output (`lua`).  This abstraction provides a simple implementation to introduce other language outputs.

A `Translator` simply provides a mapping of key value pairs, with keys being command types and values being the methods to translate them.  It implements the native Python `__call__` method, so the `Script` instance does not need to know anything about the `Translator`s internals, only that calling the instance with a key/value pair will result in the appropriate translation.

### __str__ and __repr__
For testing purposes, these methods were implemented to provide a more flexible
way to test the parsing of `yaml` files without needing to worry about comparing files written to disk or strings.

`__str__` will return the contents that would be written to disk.

`__repr__` returns a JSON output of the output data.





