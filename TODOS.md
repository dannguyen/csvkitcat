# TODOS

## priority


### csvsqueeze 

- [X] csvsqueeze: implement by-column cleaning
- [ ] break csvsqueeze into csvnorm and csvsqueeze??
- [ ] refactor csvsqueeze because it looks like spaghetti barf


## Just done


- [x] rename library to `csvkitcat`, `csvkc` for short

-----------------------

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


## csvheaders

- get list
- create
- rename
- mute/omit


## csvpad

```sh
--left 5 '0'
--right 
```

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

- csvpad
- csvsed



- csvcompute
- csvgroup

