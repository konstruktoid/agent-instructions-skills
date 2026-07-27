# uploads

Validates uploaded files before they are stored.

`uploads.naming` holds the filename helpers and the allowed extension set.
`validate_upload` calls them rather than picking a name apart itself.

## Testing

```sh
uv run pytest
```
