# -*- coding: UTF-8 -*-
"""
"""
import argparse
from collections import defaultdict, namedtuple
from io import TextIOWrapper
from pprint import pprint
from typing import List


class DummyEntity:

    def __getattr__(self, item):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __setattr__(self, key, value):
        pass


class BaseCoordinate:
    _coordinates = None

    def __init__(self, *rest, coordinates=None):
        self._coordinates = coordinates

    @property
    def coordinate(self) -> 'Coordinate':
        return self._coordinates

    @coordinate.setter
    def coordinates(self, val: 'Coordinate') -> None:
        self._coordinates = val


class BaseEntity:
    __slots__ = ()

    def __init__(self, *args):
        items = self.__class_items()
        needed = len(items)
        have = len(args)
        if needed > have:
            raise Exception(f'few params expected {self.__slots__}')
        if needed < have:
            raise Exception(f'Too many params provided for {self.__slots__}')
        for index, item in enumerate(items):
            setattr(self, item, args[index])

    def __class_items(self):
        return [item for item in self.__slots__ if not item.startswith('_')]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}{}'.format(
            self.__class__.__name__,
            {item: getattr(self, item) for item in self.__class_items()}
        )


class Junction(BaseEntity, BaseCoordinate):
    __slots__ = 'id', 'elevation', 'max_depth'

    def __str__(self):
        return f'{super().__str__()}, {self.coordinates}'


class Outfall(BaseEntity, BaseCoordinate):
    __slots__ = 'id', 'elevation', 'type'

    def __str__(self):
        return f'{super().__str__()}, {self.coordinates}'


class Conduit(BaseEntity):
    __slots__ = 'id', 'from_node', 'to_node', 'length', '_junctions', \
                '_outfalls'

    def __init__(self, *args):
        super().__init__(*args)
        self._junctions = []
        self._outfalls = []

    @property
    def outfalls(self) -> List[Outfall]:
        """

        :return:
        """
        return self._outfalls

    @property
    def junctions(self) -> List[Junction]:
        """
        :return: List
        """
        return self._junctions

    def add_junction(self, val: Junction) -> None:
        """

        :param val:
        :return:
        """
        self._junctions.append(val)

    def add_outfall(self, val: Outfall) -> None:
        """

        :param val:
        :return:
        """
        self._outfalls.append(val)

    def __str__(self):
        return f'{super().__str__()}, _junctions {self._junctions} , ' \
               f'_outfalls {self._outfalls}'


class Coordinate(BaseEntity):
    __slots__ = 'id', 'x', 'y'

    @property
    def node(self):
        return self.id


_MODEL_MAP = {
    'junctions': Junction,
    'outfalls': Outfall,
    'conduits': Conduit,
    'coordinates': Coordinate
}


def parse_file(source: TextIOWrapper) -> dict:
    """parse data from file

    :param source: TextIOWrapper
    :return: text
    """
    res = defaultdict(dict)
    group = None
    klass = None
    for line in filter(None, source):
        line = line.strip()
        if not line:
            continue
        if line[0] == '[' and line[-1] == ']':
            group = line.strip('[]').lower()
            klass = _MODEL_MAP.get(group)
            if not klass:
                raise Exception(f'Unsupported entity {group}')
            continue
        if line[0] == ';':
            print(f'Comment found {line}')
            continue
        entity = klass(*filter(None, line.split(' ')))
        res[group][entity.id] = entity
    return res


def build(**kwargs):
    """

    :param data:
    :return:
    """
    dummy = DummyEntity()
    junctions = kwargs.get('junctions', {})
    outfalls = kwargs.get('outfalls', {})
    conduits = kwargs.get('conduits', {})
    coordinates = kwargs.get('coordinates', {})
    for coordinate in coordinates.values():
        junctions.get(coordinate.node, dummy).coordinates = coordinate
        outfalls.get(coordinate.node, dummy).coordinates = coordinate

    for conduit in conduits.values():
        junction = junctions.get(conduit.from_node)
        if junction:
            conduit.add_junction(junction)
        outfall = outfalls.get(conduit.to_node)
        if outfall:
            conduit.add_outfall(outfall)

    return kwargs


if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser()
    ARG_PARSER.add_argument('infile', type=argparse.FileType('r'))
    ARGS = ARG_PARSER.parse_args()
    pprint(build(**parse_file(ARGS.infile)))
