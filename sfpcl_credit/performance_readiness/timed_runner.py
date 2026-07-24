import json
import time
import unittest

from django.test.runner import DiscoverRunner


class _TimingResult(unittest.TextTestResult):
    def startTest(self, test):
        self._performance_started_at = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        elapsed = time.perf_counter() - self._performance_started_at
        self.performance_timings.setdefault(test.id(), []).append(
            round(elapsed, 6)
        )
        super().stopTest(test)

    performance_timings = {}


class _TimingTextRunner(unittest.TextTestRunner):
    resultclass = _TimingResult


class PerformanceTimingRunner(DiscoverRunner):
    test_runner = _TimingTextRunner

    def build_suite(self, *args, **kwargs):
        discovered = super().build_suite(*args, **kwargs)
        test_ids = [test.id() for test in _flatten(discovered)]
        repeated = self.test_suite()
        for _ in range(4):
            for test_id in test_ids:
                repeated.addTests(
                    unittest.defaultTestLoader.loadTestsFromName(test_id)
                )
        return repeated

    def run_suite(self, suite, **kwargs):
        _TimingResult.performance_timings = {}
        result = super().run_suite(suite, **kwargs)
        print(
            "PERFORMANCE_TIMINGS_JSON="
            + json.dumps(
                result.performance_timings,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return result


def _flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _flatten(test)
        else:
            yield test
