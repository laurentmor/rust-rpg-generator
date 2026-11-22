import unittest
from prepare_release import verify, COMMANDS

class ReleaseGateTests(unittest.TestCase):
    def valid(self):
        return dict(python_tests=True, generation=True, cargo_available=True, rust_verified=True,
                    status='rust_verified', audit=dict(levels=120, cargo_checked=360,
                    cargo_verified=True, status='rust_verified', missing_branches=[],
                    invalid_branches=[], content_failures=[], cargo_failures=[],
                    cargo_results=[dict(branch=f'level-{n:03d}/solutions', command=cmd, exit_code=0)
                                   for n in range(1, 121) for cmd in sorted(COMMANDS)]))
    def test_valid(self):
        self.assertEqual(verify(self.valid()), [])
    def test_missing_check(self):
        report = self.valid()
        report['audit']['cargo_results'].pop()
        self.assertTrue(verify(report))
    def test_duplicate_check(self):
        report = self.valid()
        report['audit']['cargo_results'][-1] = report['audit']['cargo_results'][0]
        self.assertTrue(verify(report))
    def test_failed_command(self):
        report = self.valid()
        report['audit']['cargo_results'][0]['exit_code'] = 101
        self.assertTrue(verify(report))
    def test_false_status(self):
        report = self.valid()
        report['rust_verified'] = False
        self.assertTrue(verify(report))

if __name__ == '__main__':
    unittest.main()
