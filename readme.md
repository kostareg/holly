## Notes

```
uv run holly_server # run the server
uv run pytest       # run tests
ruff check          # run lints
```

`.git/hooks/pre-commit`:

```
( cd web && biome check )
ruff check
uv run pytest
```
