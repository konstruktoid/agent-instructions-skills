# reportkit

Exports stored reports.

## Usage

```sh
python -m reportkit.export --output reports.csv
```

Only CSV output is reachable from the command line. `write_html` in
`reportkit.export` shows the conversion path: it writes an intermediate CSV file
and hands it to pandoc through the shared helpers in `reportkit.shellutils`,
which is where quoting, command building, and temporary files are dealt with for
every conversion.
