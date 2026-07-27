# tempo

Date helpers.

`HOLIDAYS` in `tempo.calendar` lists the company holidays and `is_holiday`
answers whether a date is one of them. Day arithmetic goes through
`days_between`, whose docstring states which ends it counts.

## Testing

```sh
uv run pytest
```
