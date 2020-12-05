# z88dk-sym
A debugging utility to manage z88dk's *.lis and *.map files into locating symbols and line addresses

### How to install
```bash
pip install git+https://github.com/desertkun/z88dk-sym
```

### Prepare your z88dk project

1. Make sure your object files (.c) are compiled with `--list --c-code-in-asm` flags. 
   Compiles should emit .lis files in the source folder by default
2. Make sure the main executable is compiled with `-gen-map-file`
   The compiler should also produce the .map file for the executable

### How to locate a line number by an absolute address

```bash
python -m z88dk.sym --lists="src/zx" --map bin/z4chan.map who --location 82ED
> Location 82ED points at src:_main:31
```

### Speed up the process

```
# generate the db (e.g. in a makefile)
python -m z88dk.sym --lists="src/zx" dump --dump-to db.json
# reuse the db
python -m z88dk.sym --db db.json --map bin/z4chan.map who --location 82FF
Location 82FF points at src:_main:37
```