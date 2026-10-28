# Span Desk

Span Desk checks a drafted, cited answer. This repository currently contains only the deterministic figure check.

A claim figure that does not appear in the retrieved snippet is `unsupported`. A later model call must not upgrade that result. Claims with no digit figure are `not_applicable`, and the model may still judge the paraphrase later. Currency symbols, percent signs, and thousands commas are ignored when comparing the figure itself. Spelled-out numbers such as "thirty" do not count.

These tests use synthetic sentences in `tests/fixtures/number_cases.json`. They are not live Tavily retrievals and not a measure of citation accuracy.

## Run the tests

From this directory:

```shell
python -m unittest discover -s tests -v
```

No API key and no network call are required.
