import argparse
import json
from .lis import Z88DKList
from .map import Z88DKMap

parser = argparse.ArgumentParser(description='Analyzes debugging symbols for z88dk')

parser.add_argument('--lists', type=str, nargs='+', help='Paths to a folders with *.lis files')
parser.add_argument('action', type=str, help='Action to perform', choices=["dump", "who"])
parser.add_argument('--map', type=str, help='The map file for the executable')
parser.add_argument('--dump-to', type=str, help='dump: a file name to dump the database')
parser.add_argument('--db', type=str, help='Load database from this file')
parser.add_argument('--location', type=str, help='who: hex location')

args = parser.parse_args()

z88dk_map = None
z88dk_list = Z88DKList()

if args.db:
    with open(args.db, "r") as f:
        z88dk_list.load(json.load(f))
else:
    if not args.lists:
        raise RuntimeError("At least one list must be specified")
    for arg_list in args.lists:
        z88dk_list.parse(arg_list)

if args.map:
    z88dk_map = Z88DKMap(args.map)
    z88dk_map.enhance(z88dk_list)


def action_dump():
    if args.dump_to is None:
        raise RuntimeError("--dump-to is not specified")

    with open(args.dump_to, "w") as f:
        json.dump(z88dk_list.dump(), f)


def action_who():
    if z88dk_map is None:
        raise RuntimeError("Map file is not specified")
    if args.location is None:
        raise RuntimeError("Location is not specified")

    location_int = int(args.location, 16)
    located = z88dk_map.locate(location_int)

    if located:
        symbol, line = located
        print("Location {0} points at {1}:{2}:{3}".format(args.location, symbol.sym.file_name, symbol.sym.name, line))
    else:
        print("Cannot find symbol at location")


if args.action == "dump":
    action_dump()
elif args.action == "who":
    action_who()
else:
    raise RuntimeError("Unknown action")
