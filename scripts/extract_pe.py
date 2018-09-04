#!/usr/bin/env python2
'''
Extract byte arrays starting with an MZ header from .NET BinaryFormatter'd data.

author: Willi Ballenthin
email: william.ballenthin@fireeye.com
'''
import sys
import hashlib
import logging

import argparse

import dnbinaryformat


logger = logging.getLogger(__name__)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Extract byte arrays starting with an MZ header from .NET BinaryFormatter'd data.")
    parser.add_argument("input", type=str,
                        help="Path to input file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Disable all output but errors")
    args = parser.parse_args(args=argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger().setLevel(logging.INFO)


    with open(args.input, 'rb') as f:
        buf = f.read()

    records = dnbinaryformat.deserialize(buf)
    for i, (_, record) in enumerate(records):
        if int(record.RecordTypeEnum) != dnbinaryformat.RecordTypeEnumerator.ArraySinglePrimitive:
            continue
        logger.info('record %d: found array', i)

        if record.PrimitiveTypeEnum != dnbinaryformat.PrimitiveTypeEnumeration.Byte:
            continue
        logger.info('record %d: found byte array', i)

        buf = bytes(record.Value)
        if not buf.startswith(b'MZ'):
            continue
        logger.info('record %d: found PE byte array', i)

        m = hashlib.md5()
        m.update(buf)
        filename = m.hexdigest() + '.bin'

        logger.info('writing PE to %s', filename)
        with open(filename, 'wb') as f:
            f.write(buf)

    return 0


if __name__ == "__main__":
    sys.exit(main())
