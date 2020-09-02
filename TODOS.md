# TODOS

# PRIORITY NEXT


- csvgroupby 
  - needs more documentation



- csvchart
  - [x] with no parameters, create a bar chart, with the x-column being the first Text column, and the y-column being the first Number column
  - default: terminal bar chart
    - takes x-col and y-col
    - prints to terminal
  - SVG mode
    - [ ] write to file and open immediately
    - charts
      - bar_chart: https://agate.readthedocs.io/en/1.6.1/cookbook/charting.html#svg-bar-chart
      - column_chart: https://agate.readthedocs.io/en/1.6.1/cookbook/charting.html#svg-column-chart
      - line_chart: https://agate.readthedocs.io/en/1.6.1/cookbook/charting.html#svg-line-chart
      - scatterplot: https://agate.readthedocs.io/en/1.6.1/cookbook/charting.html#svg-dots-chart
      - lattice: https://agate.readthedocs.io/en/1.6.1/cookbook/charting.html#svg-lattice-chart
        - tricky because it expects a group_by aggregation to be specified 
  

  - external libs
    - stacked chart, histogram, multi-variable: https://github.com/mkaz/termgraph

- csvslice
  - wtf is this terrible and inefficient code? `rowslice = list(myio.rows)[slice_start:slice_end]`
`  

- csvbin: https://agate.readthedocs.io/en/1.3.1/api/table.html#agate.Table.bins

- csvuniq:
  - utility to calculate ordinality
  - shortcut for `csvcut -c category | sort | uniq -c | sort -rn`
  - look at how `csvstat` and `xsv frequency` does it
  - https://agate.readthedocs.io/en/1.6.1/cookbook/filter.html#distinct-values
  
- csvround
  - for numbers, round by integer and precision
  - for dates, perform strftime
  - for text, truncate

- Content and guides
  - Real-world scenarios
    - for babynames, do a trend: csvstack, csvchart, csvpivot
    - Count crime types by year: csvround, csvpivot
    - Extract mentions from tweets by date: csvround, csvxtract (requires a util to denormalize?)
  - Tool page
    - [ ] Each description section should have a h3:Example subsection


- csvnorm
  - need flag for just minimal space-fixing, e.g. `--min/--lite`, for translit stuff

- csvrange
  - use builtin Agate examples: https://agate.readthedocs.io/en/1.6.1/cookbook/filter.html#values-within-a-range

- Categorize utils:
    - inspection: csvcount, csvflatten
    - transformation: csvnorm, csvsed, csvpad?
    - augmentation, csvxcap/xfind/xsplit, 
    - computation: csvpivot, csvchart, csvround?
    - filtering: csvslice, csvrange?



In general:

- [ ] clean up code with Black
  - [x] some tests blacked
- [ ] refactor tests, add tests to validate specific examples in documentation
  


## Lesser priority/maybe deprioritize


consider usecase for integrating clevercsv: https://github.com/alan-turing-institute/CleverCSV

csvcount
- [X] change basic behavior to output rows,cells,empty_rows,empty_cells
  - [ ] Refactor the resulting spaghetti code and nested logic
-  pattern matching `-p [pattern]`
  - [X] given a list of [PATTERN], return row and column count that contain [PATTERN]
  - [X] return list of total matches, as some cells have more than one cell


csvsed

- [ ] remove boilerplate/unnecessary arguments. Should defer as much as possible to csvformat
- [ ] benchmarking....majorly slow as hell: tests/benchmark/rawsed.py
- [x] --whole option: match and replace entire field instead
  - [?] unfortunately I did it brute force dumb way and it is substantially slower than non--whole
  - [ ] sketch out usecases for whole-cell match/replace, compare to Excel


csvpad
- [ ] basic implementation and tests
    ```sh
    --left 5 '0'
    --right 
    ```


csvxplit
- [ ] advanced feature: --max-split: make the number of new split columns based on the max number of splits found. Requires basically iterating through twice...


csvflatten, csvcount
- [ ] Major revamps were done, need to come up with more robust tests to make sure all weird edgecases are covered.


csvxfind, csvxcap
- Provide option to specify prefix? 


csvpivot

- https://agate.readthedocs.io/en/1.6.1/api/table.html#agate.Table.pivot
- [ ] option to sort? But is that even useful when doing just a column pivot? How about ordering columns alphabetically/numerically too? `--sort-row` `--sort-col` `a,z,n,0`
- [ ] grand total column and row?

- Table.pivot() params to consider:
  - default_value – Value to be used for missing values in the pivot table. Defaults to Decimal(0). If performing non-mathematical aggregations you may wish to set this to None.





### Just done


- csvgroupby: csvpivot doesn't allow for multiple value calculations, e.g `SELECT country, MAX(age), MEAN(age) FROM data GROUP BY country`
  - https://agate.readthedocs.io/en/1.6.1/api/table.html#agate.Table.group_by
  - basic implementation
    - [X] needs more tests
    - [X] defaults to `Count()`; `-a/--aggs` needs to parse multiple functions, e.g. `--agg "Optional column name|sum:age`
    - [X] do ColumnIdentifierError when attempting to aggregate invalid column name

- csvpivot: fixing how --agg works and is delimited:
  - [x] `--agg sum:age` instead of `--agg sum,age`
  - [x] `--agg list` to get list of stuff

csvpivot
- [x] basic implementation and tests
  - [x] the `-r` param takes in multiple comma-delimited fields
- [x] default counting behavior
- [x] add support for other aggregations


csvflatten
- [X] Independently handle newlines

csvxplit
- [X] basic implementation and testing

csvxcap
- like csvxplit, except creates columns based on captured groups
- [x] basic implementation

csvxtract/xfind
- ???: does a regex.findall, and group concats them into a column?
- [x] basic implementation

-----------------------

## on deck/non-priority

## csvslice
  - [ ] csvhead: basically a reskin of csvslice
  - [ ] csvtail: not trivial, will need to research this
  - read up on csvkit followup issue: https://github.com/wireservice/csvkit/issues/669


## in general

- [x] rename csvkitcat.utils_plus to moreutils
- [ ] how should i deal with `override_flags`?
- [ ] extract/abstract boilerplate csvwriter args stuff, via csvflatten and csvsed
- [ ] add skip-line functionality to csvsqueeze, slice, etc
- [ ] print out separate version number

## csvcount

- [ ] kill unnecessary arguments
  - [?] partially did this by looking at `csvkit.cli._init_common_parser(self)`
  - [x] added custom `_extract_csv_reader_kwargs` to alltext.py, with a third argument to `getattr` to prevent error

- [ ] copy https://csvkit.readthedocs.io/en/latest/scripts/csvstat.html
    ```py
            if self.args.count_only:
            count = len(list(agate.csv.reader(self.skip_lines(), **self.reader_kwargs)))

            if not self.args.no_header_row:
                count -= 1

            self.output_file.write('Row count: %i\n' % count)

            return
    ```
- [x] basic implemention
- [x] edge cases with negative start/end
- [x] basic error cases

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
# DRAFT STUFF/dumb ideas

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




## csvreplace

like `csvsed`, except replaces entire column

```
--columns
--pattern
--output '$1'
```


### csvfind (already done by csvcount)

- for every row, count number of matches with given pattern
- create column with find_count
- create column with find_extracts: line for every match




## old todos


csvsqueeze->csvnorm

- [X] pass newly refactored tests
- [?] refactor csvsqueeze because it looks like spaghetti barf
    - [ ] mostly did this
- [X] add norm-casing
- add toggle type options? https://stackoverflow.com/questions/34735831/python-argparse-toggle-no-toggle-flag




- csvslice
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
