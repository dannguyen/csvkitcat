# TODOS

# PRIORITY




## csvcount 

- [ ] kill unnecessary arguments
  - [?] partially did this by looking at `csvkit.cli._init_common_parser(self)`
  - [x] added custom `_extract_csv_reader_kwargs` to alltext.py, with a third argument to `getattr` to prevent error



### csvsqueeze 

- [ ] break csvsqueeze into csvnorm and csvsqueeze??
- [ ] refactor csvsqueeze because it looks like spaghetti barf




## Lesser priority/maybe deprioritize



## csvpad

- [ ] basic implementation and tests

```sh
--left 5 '0'
--right 
```



## csvsed

- [ ] benchmarking....majorly slow as hell: tests/benchmark/rawsed.py
- [x] --whole option: match and replace entire field instead
  - [ ] unfortunately I did it brute force dumb way and it is slower than non--whole





### Just done

- csvindex
  - [X] `--index` option; Slice a single record (shortcut for --is N --len 1).
  - [X] reconsider option names --is and --ie
    - [x] changed to -S, -E, -L


- csvsed
  - [x] basic test and implementation
  - [x] -m for literal match
  - [x] --max for limiting number of matches per field

- csvsqueeze
  - [X] implement by-column cleaning
  
-- general
  - [x] rename library to `csvkitcat`, `csvkc` for short
  - [x] created alltextutil for common case of reading just text


-----------------------

## on deck/non-priority

## csvslice
  - [ ] csvhead: basically a reskin of csvslice
  - [ ] csvtail: not trivial, will need to research this



## in general

- [x] rename csvkitcat.utils_plus to moreutils
- [ ] how should i deal with `override_flags`?
- [ ] extract/abstract boilerplate csvwriter args stuff, via csvflatten and csvsed
- [ ] add skip-line functionality to csvsqueeze, slice, etc
- [ ] print out separate version number

## csvcount

- [x] basic implemention
- [x] edge cases with negative start/end
- [x] basic error cases
- [ ] copy https://csvkit.readthedocs.io/en/latest/scripts/csvstat.html
    ```py
            if self.args.count_only:
            count = len(list(agate.csv.reader(self.skip_lines(), **self.reader_kwargs)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('Row count: %i\n' % count)

            return
    ```

## csvflatten

- `--row-id` add row_id column (line number?)
- chop new rows for every new line? (make new test file)
- any need to remove unnecessary arguments from base CSVKitUtility?
- csvflatten should have inference
- how does typecasted values work?
- make sure 2.x and 3.x compatible

- [X] write tests
- [x] why do I have to set quote mode to 1 when working with examples/longvals.csv?
- [na] add flag to do max-length record breaking, but in newline mode (e.g. ideal for spreadsheets)
    - Don't need this because in spreadsheets, users can format column width vidsually


## csvsqueeze

- implement by character stripping
    - pass args to lstrip, rstrip










------------------------------
------------------------------
------------------------------
------------------------------
------------------------------
# DRAFT STUFF

## csvheaders

- get list
- create
- rename
- mute/omit



## csvblob


output record_id,record

```
  
  [[rowid]]
  1  

  [[date]]
        
  [[name]]
  
  [[whatever]]

```

## csvtxtval newcol from regex

- create only one new column
- requires `--output` pattern
- ignores --max-matches
- colname is srccolumn_extract



csvtxform: makes 1 column from one regex pattern:
    - if no --output, then new column is what was matched
    - if --output, then new column is that pattern
    - if --by-groups, then make new columns; ignores --output

csvtxract: makes new columns, or 1 column
    - by delimiter
    - by named capture



## csvtxt


```
csvtxcap [subcommand] [pattern] --regex --xname

--pattern
--regex is pattern literal or regex
--column column to target
--output-header 
--max-matches: number of extractions
--match-delimiter: '\n» '
```



- collect/serialize (as yaml?)
    - provide a pattern
        - create n columns, for the first n finds
    - provide a pattern with named captured groups
        - max-count is assumed to be 0
        - create column for every group: "[src_column] _ [group_name]"


- colsplit
    - split by literal delimiter, create n columns
    - split by regex pattern

- split


## csvtextsplit
given a column and a delimiter, create n columns



## csvreplace

like `csvsed`, except replaces entire column

```
--columns
--pattern
--output '$1'
```


### csvfind

- for every row, count number of matches with given pattern
- create column with find_count
- create column with find_extracts: line for every match

### csvpick/csvfrak/csvxtract/csvrx

#### csvgsplit/csvcapture


## other stuff

- csvfreq/csvcount


- csvslice
    - csvhead
    - csvtail
- csvrange

- csvcompute
- csvgroup

