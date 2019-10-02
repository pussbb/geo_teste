# -*- coding: UTF-8 -*-
"""
"""
import argparse
from collections import defaultdict, namedtuple
from io import TextIOWrapper
from pprint import pprint


class Junction(namedtuple('Junction', ['name', 'elevation', 'max_depth'])):
    pass


class Outfall(namedtuple('Outfall', ['name', 'elevation', 'type'])):
    pass


class Conduit(namedtuple('Conduit',
                         ['name', 'from_name', 'to_node', 'length'])):
    pass


class Outfall(namedtuple('Outfall', ['name', 'elevation', 'type'])):
    pass


class Coordinate(namedtuple('Coordinate', ['node', 'x', 'y'])):
    pass


_MODEL_MAP = {
    'JUNCTIONS': Junction,
    'OUTFALLS': Outfall,
    'CONDUITS': Conduit,
    'COORDINATES': Coordinate
}


def parse_file(source: TextIOWrapper) -> dict:
    """parse data from file and return raw data as dict

    :param source: TextIOWrapper
    :return: text
    """
    res = defaultdict(list)
    group = None
    for line in filter(None, source):
        line = line.strip()
        if not line:
            continue
        if line[0] == '[' and line[-1] == ']':
            group = line.strip('[]')
            continue
        if line[0] == ';':
            print(f'Comment found {line}')
            continue
        res[group].append(filter(None, line.split(' ')))
    return res


def build(data: dict):
    """

    :param res:
    :return:
    """
    if not _MODEL_MAP.keys() >= data.keys():
        raise Exception(f'Invalid file format,'
                        f' model difference {_MODEL_MAP.keys() ^ data.keys()}')

    res = defaultdict(list)
    for name, klass in _MODEL_MAP.items():
        res[name] = [klass(*item) for item in data.get(name, [])]
    pprint(res)


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument('infile', type=argparse.FileType('r'))
    ARGS = ARG_PARSER.parse_args()
    build(parse_file(ARGS.infile))