
"""jsonlist.py

This module is used to read and write JSON-List files.

A JSON-List file is a text file that every line is a JSON string.

For example, a JSON-List file named test.jl has the following content:

    {"foo": "bar"}
    {"a": 123, "b": 456}

So that it can be loaded into python as a list of dicts:

    $ python3
    >>> import jsonlist
    >>> jsonlist.load_file('test.jl')
    [{'foo': 'bar'}, {'a': 123, 'b': 456}]

And a list of dicts can be dumped into a JSON-List file.

    $ python3
    >>> import jsonlist
    >>> jlist = [{'foo': 123, 'bar': 456}, {'hello': 'python'}, {}]
    >>> jsonlist.dump_file(jlist, 'output.jl')
    >>> exit()
    $ cat output.jl
    {"bar": 456, "foo": 123}
    {"hello": "python"}
    {}

"""

import io
import sys
import json

def dumps(jlist):
    """Dump jlist into a str object."""
    lines = []
    for obj in jlist:
        lines.append(json.dumps(obj) + '\n')
    return ''.join(lines)

def dump(jlist, stream):
    """Dump jlist into an IO stream."""
    for obj in jlist:
        stream.write(json.dumps(obj) + '\n')

def dump_file(jlist, file_path):
    """Dump jlist into a file."""
    with open(file_path, 'w') as stream:
        dump(jlist, stream)

def str_list_from_data(data):
    """Turn data into a str generator."""
    for line in data.split('\n'):
        yield line

def str_list_from_io(stream):
    """Turn stream into a str generator."""
    while True:
        line = stream.readline()
        if line == '':
            break
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        yield line

def str_list(source):
    """Turn source into a str generator."""
    if isinstance(source, str):
        return str_list_from_data(source)
    elif isinstance(source, io.IOBase):
        return str_list_from_io(source)
    else:
        raise TypeError('unsupported source type')

def parse_line(line):
    """Parse a JSON string into a Python object."""
    try:
        line = line.strip()
        return json.loads(line)
    except json.decoder.JSONDecodeError:
        return None

def load_str_list(str_gen):
    """Load JSON list from a list of strings."""
    result = []
    for line in str_gen:
        if line == '':
            break
        obj = parse_line(line)
        if obj is not None:
            result.append(obj)
    return result

def loads(data):
    """Load JSON list from a trunk of data."""
    return load_str_list(str_list(data))

def load(stream):
    """Load JSON list from an IO stream."""
    return load_str_list(str_list(stream))

def load_file(file_path):
    """Load JSON list from a file."""
    with open(file_path) as stream:
        return load(stream)

def main():
    """Load a JSON-List file and print the parsed content."""
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: jsonlist.py input_file\n')
        exit(1)

    jlist = load_file(sys.argv[1])
    for obj in jlist:
        print(obj)

if __name__ == '__main__':
    main()
