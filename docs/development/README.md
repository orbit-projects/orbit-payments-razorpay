# Razorpay adapter development

Install the capability checkout first:

```bash
python -m pip install -e ../orbit-payments
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy
```

Keep tests deterministic with injected fake SDK resources and signed synthetic webhook payloads.
Never use live credentials in CI. Provider test-mode smoke checks are separate release gates.
