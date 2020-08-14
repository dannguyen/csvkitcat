# TODOS

## General

- rename library to `csvkitcat`, `csvkc` for short


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

- implement by-column cleaning
- implement by character stripping
    - pass args to lstrip, rstrip


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

## csvrextract

(by column?)

```sh
--newcolname
--simple-pattern
--match-delimiter

--pattern
--output-replace
```

### csvpcount

- for every row, count number of matches with given patterns
- more than one pattern can be sought
- option to create column per pattern
    pcount_01_slug




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

