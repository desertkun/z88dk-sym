# z88dk-sym
A debugging utility to manage z88dk's *.lis and *.map files into locating symbols and line addresses

### How to install
```bash
pip install git+https://github.com/desertkun/z88dk-sym
```

### Prepare your z88dk project

1. Make sure your object files (.c) are compiled with `--list --c-code-in-asm` flags. 
   Compiles should emit .lis files in the source folder by default.
   Beware that this might increase the binary footprint because of partially
   ineffective copt rules.
2. Make sure the main executable is compiled with `-gen-map-file`
   The compiler should also produce the .map file for the executable

### Generate the debug database

Could be part of build process (e.g. with a Makefile)

```bash
# generate the db (e.g. in a makefile)
python -m z88dk.sym dump --dump-to <db file> --lists <folders with .lis files>
# e.g.
python -m z88dk.sym dump --dump-to db.json --lists "src/zx1" "src/zx2" 
```

### How to locate a line number by an absolute address

```bash
python -m z88dk.sym --db db.json --map bin/z4chan.map addr2loc --location 82ED
> Location 82ED points at src/main.c:_main:31
```

### How to locate an absolute address by given file name and line

```bash
python -m z88dk.sym --db db.json --map bin/z4chan.map loc2addr --source src/main.c --line 31
> Location src/zx/main.c:31 points at 0x82ed
```

### How to locate an absolute address of given function

```bash
python -m z88dk.sym --db db.json --map bin/z4chan.map loc2addr --symbol _main
> Location _main points at 0x82c3
```
