#!/usr/bin/env python3
"""Fail-closed release evidence gate; does not claim to rerun Cargo."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

COMMANDS = {'cargo fmt --check', 'cargo clippy --workspace --all-targets -- -D warnings', 'cargo test --workspace'}


def verify(report: dict) -> list[str]:
    errors = []
    for field in ('python_tests', 'generation', 'cargo_available', 'rust_verified'):
        if report.get(field) is not True:
            errors.append(f'{field} must be true')
    if report.get('status') != 'rust_verified':
        errors.append('status must be rust_verified')
    audit = report.get('audit')
    if not isinstance(audit, dict):
        return errors + ['audit object missing']
    if audit.get('levels') != 120 or audit.get('cargo_checked') != 360 or audit.get('cargo_verified') is not True:
        errors.append('expected 120 levels and 360 verified Cargo checks')
    if audit.get('status') != 'rust_verified':
        errors.append('audit status must be rust_verified')
    for field in ('missing_branches', 'invalid_branches', 'content_failures', 'cargo_failures'):
        if audit.get(field) != []:
            errors.append(f'{field} must be an empty list')
    results = audit.get('cargo_results')
    if not isinstance(results, list) or len(results) != 360:
        return errors + ['cargo_results must contain exactly 360 entries']
    expected = {(f'level-{n:03d}/solutions', cmd) for n in range(1, 121) for cmd in COMMANDS}
    actual = set()
    for item in results:
        if not isinstance(item, dict) or item.get('exit_code') != 0:
            errors.append('Cargo result contains nonzero or invalid entry')
            continue
        key = (item.get('branch'), item.get('command'))
        if key in actual:
            errors.append(f'duplicate Cargo result: {key}')
        actual.add(key)
    if actual != expected:
        errors.append(f'Cargo coverage mismatch: {len(expected-actual)} missing, {len(actual-expected)} unexpected')
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description='Validate external Windows release evidence and produce a checksum manifest')
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--output', type=Path, default=Path('release-manifest.json'))
    args = p.parse_args()
    try:
        report_bytes = args.report.read_bytes()
        report = json.loads(report_bytes)
        artifact_bytes = args.artifact.read_bytes()
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    errors = verify(report)
    if errors:
        for error in errors:
            print('FAIL:', error)
        return 1
    manifest = {
        'release_status': 'candidate',
        'rust_verification': 'verified by supplied external Windows report (not rerun here)',
        'levels': 120,
        'cargo_checks': 360,
        'report': {'filename': args.report.name, 'sha256': hashlib.sha256(report_bytes).hexdigest()},
        'artifact': {'filename': args.artifact.name, 'sha256': hashlib.sha256(artifact_bytes).hexdigest()},
        'manual_smoke_test': 'pending',
    }
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('PASS: report contains 360 distinct successful checks; release remains candidate until manual smoke test')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
