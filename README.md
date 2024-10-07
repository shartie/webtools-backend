
```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v2.3.0
  hooks:
  -   id: check-yaml
  -   id: end-of-file-fixer
  -   id: trailing-whitespace
- repo: https://github.com/astral-sh/ruff-pre-commit
  # Ruff version.
  rev: v0.6.9
  hooks:
    # Run the linter.
    - id: ruff
    # Run the formatter.
    - id: ruff-format
```

```bash
# add pre-commit to deps
poetry run pre-commit install
poetry run pre-commit run   --all-files
```

```bash
python main.py
```

```bash
curl -N -X POST \
     -H "Content-Type: application/json" \
     -d '{"text": "your_text_here"}' \
     http://localhost:8080/api/summary/create
```


```bash
curl -X POST "http://localhost:8000/summaries/" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Understanding Async in Python",
           "short_description": "A deep dive into asynchronous programming in Python.",
           "content": "# Async in Python\nAsynchronous programming is ...",
           "authors": ["Alice Smith", "Bob Johnson"]
         }'
```


```
curl -X GET "http://localhost:8080/api/summaries/dcc7e7b3-f39a-47ff-976e-90ea9ecb65d1" -H "accept: application/json"
```
