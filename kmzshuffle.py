#!/usr/bin/env python3

import argparse
import pathlib
import random
import re
import zipfile


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


DEFAULT_IN_FILE: pathlib.Path = pathlib.Path('./places.kmz').resolve()
KMZ_DOC_FILENAME: str = 'doc.kml'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == '__main__':
    # setup argparser
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', metavar='FILEPATH', type=pathlib.Path, default=DEFAULT_IN_FILE, help=f'path to the kmz file to read, default: <current_working_directory>/places.kmz')
    argparser.add_argument('-y', action='store_true', default=False, help=f'do not ask for confirmation before starting, default: ask for confirmation')

    # parse given args
    args: argparse.Namespace = argparser.parse_args()

    # resolve and check input file path
    in_file: pathlib.Path = pathlib.Path(args.i).resolve()
    if not args.i.is_file():
        print(f'input file not found: {args.i}')
        exit(1)

    # bake output and temporary file path
    out_file: pathlib.Path = pathlib.Path(args.i.parent / f"{args.i.name.replace(args.i.suffix, '')}_shuffled{args.i.suffix}").resolve()
    tmp_file: pathlib.Path = pathlib.Path(args.i.parent / '___tmp___.kml').resolve()

    # print some useful info and require confirmation before starting
    print('shuffle placemarks ...', end='\n\n')
    print('    input file:', in_file)
    print('temporary file:', tmp_file)
    print('   output file:', out_file, end='\n\n')
    try:
        if not args.y and not input('Do it? [Y/n]: ').lower().strip() == 'y':
            exit()
    except KeyboardInterrupt:
        print()
        exit()

    # read input file
    with zipfile.ZipFile(in_file, 'r') as zip_file:
        with zip_file.open(KMZ_DOC_FILENAME) as doc_file:
            doc: str = doc_file.read().decode()

    # collect all <Placemark>'s
    shuffled_placemarks: list[str] = [v for v in re.findall('(<Placemark>.*?</Placemark>)', doc, flags=re.DOTALL)]

    # shuffle collected placemarks
    random.shuffle(shuffled_placemarks)

    # delete all placemarks entry from tmp doc
    doc = re.sub('<Placemark>.*</Placemark>', '', doc, flags=re.DOTALL)

    # add marker for insert
    doc = re.sub('</Folder>', '---placemarks---\n</Folder>', doc)

    # insert shuffled placemarks
    doc = re.sub('---placemarks---', '\n'.join(shuffled_placemarks), doc)

    # write tmp doc
    tmp_file.write_text(doc)

    # zip to kmz
    with zipfile.ZipFile(out_file, 'w') as zip_file:
        zip_file.write(filename=tmp_file, arcname=KMZ_DOC_FILENAME)
        print(f'wrote {tmp_file.stat().st_size} bytes to {out_file}')
        # delete tmp doc
        tmp_file.unlink()
