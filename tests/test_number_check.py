"""Fixture tests for the deterministic figure check.

The JSON cases are synthetic text, not live Tavily retrievals.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from span_desk.number_check import check_numbers  # noqa: E402

CASES = json.loads((ROOT / "tests" / "fixtures" / "number_cases.json").read_text(encoding="utf-8"))


class NumberCheckTests(unittest.TestCase):
    def test_fixture_cases(self) -> None:
        self.assertGreaterEqual(len(CASES), 10)
        for case in CASES:
            with self.subTest(case=case["id"]):
                result = check_numbers(case["claim"], case["snippet"])
                self.assertEqual(result.status, case["status"])
                self.assertEqual(result.model_may_set_support, case["model_may_set_support"])
                self.assertEqual(list(result.claim_numbers), case["claim_numbers"])
                self.assertEqual(list(result.missing_numbers), case["missing_numbers"])

    def test_unsupported_cannot_be_upgraded(self) -> None:
        result = check_numbers("The prize is $12,000.", "The prize is $11,000.")
        self.assertEqual(result.status, "unsupported")
        self.assertFalse(result.model_may_set_support)

    def test_non_string_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            check_numbers("The cap is 1,000.", None)  # type: ignore[arg-type]

    def test_module_does_not_reference_network_clients(self) -> None:
        source = (ROOT / "src" / "span_desk" / "number_check.py").read_text(encoding="utf-8")
        for blocked in ("urllib", "socket", "httpx", "requests", "tavily", "openai"):
            self.assertNotIn(blocked, source)


if __name__ == "__main__":
    unittest.main()
