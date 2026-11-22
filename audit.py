#!/usr/bin/env python3
"""Read-only structural audit and optional isolated Cargo validation of Rust RPG."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

LEVELS = range(1, 121)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True)


def source(repo: Path, branch: str, filename: str) -> str | None:
    result = git(repo, 'show', f'{branch}:{filename}')
    return result.stdout if result.returncode == 0 else None


def audit(repo: Path, cargo: bool = False, progress=None) -> dict:
    if not (repo / '.git').exists():
        raise ValueError(f'Not a Git repository: {repo}')
    if cargo and not shutil.which('cargo'):
        raise RuntimeError('Cargo not installed; --cargo cannot certify Rust solutions')
    branches_result = git(repo, 'branch', '--format=%(refname:short)')
    if branches_result.returncode:
        raise RuntimeError(branches_result.stderr)
    branches = set(branches_result.stdout.splitlines())
    report = {
        'levels': 120, 'missing_branches': [], 'invalid_branches': [],
        'content_failures': [], 'cargo_failures': [], 'cargo_checked': 0,
        'cargo_requested': cargo, 'cargo_verified': False, 'cargo_results': [],
    }
    def emit(event: str, **fields) -> None:
        if progress is not None:
            progress(event, **fields)

    emit('audit_start', total_levels=120, total_checks=360 if cargo else 0)
    # Read-only inspections work even with uncommitted player work and do not
    # change the active branch. Never run a solution inside the player's tree.
    for level in LEVELS:
        prefix = f'level-{level:03d}'
        emit('level_start', level=level, total=120)
        for kind in ('work', 'solutions'):
            branch = f'{prefix}/{kind}'
            if branch not in branches:
                report['missing_branches'].append(branch)
                continue
            manifest = source(repo, branch, 'Cargo.toml')
            brief = source(repo, branch, 'LEVEL.md')
            if not manifest or not brief or f'Level {level:03d}' not in brief and f'Niveau {level:03d}' not in brief:
                report['invalid_branches'].append(branch)
            # The capstone is a multi-crate workspace; others use src/lib.rs.
            code_path = 'crates/rpg-core/src/lib.rs' if level == 120 else 'src/lib.rs'
            code = source(repo, branch, code_path)
            if not code:
                report['invalid_branches'].append(f'{branch}:{code_path}')
                continue
            if kind == 'work' and 'todo!' not in code:
                report['content_failures'].append(f'{branch}: missing starter TODO')
            if kind == 'solutions' and ('todo!' in code or 'unimplemented!' in code):
                report['content_failures'].append(f'{branch}: incomplete solution')
            if kind == 'solutions' and '#[test]' not in code and level != 120:
                report['content_failures'].append(f'{branch}: missing acceptance test')
            if level % 10 == 0 and 'Integration challenge' not in brief and 'Défi intégrateur' not in brief:
                report['content_failures'].append(f'{branch}: missing boss guide')
            if level % 10 == 0 and level != 120:
                boss_code = source(repo, branch, 'src/boss.rs')
                if not boss_code or 'boss_acceptance' not in boss_code:
                    report['content_failures'].append(f'{branch}: missing executable boss challenge')
                elif kind == 'work' and 'todo!' not in boss_code:
                    report['content_failures'].append(f'{branch}: missing boss starter TODO')
                elif kind == 'solutions' and ('todo!' in boss_code or 'unimplemented!' in boss_code):
                    report['content_failures'].append(f'{branch}: unfinished boss solution')
                if 'pub mod boss;' not in code:
                    report['content_failures'].append(f'{branch}: boss module not exported')
            if kind == 'solutions' and cargo:
                # A disposable worktree avoids touching the user's active branch,
                # including when the user has uncommitted work.
                with tempfile.TemporaryDirectory(prefix='rust-rpg-audit-') as temp:
                    target = Path(temp) / 'solution'
                    added = git(repo, 'worktree', 'add', '--quiet', '--detach', str(target), branch)
                    if added.returncode:
                        report['invalid_branches'].append(f'{branch}: worktree failed: {added.stderr[-400:]}')
                        continue
                    try:
                        commands = [
                            ['cargo', 'fmt', '--check'],
                            ['cargo', 'clippy', '--workspace', '--all-targets', '--', '-D', 'warnings'],
                            ['cargo', 'test', '--workspace'],
                        ]
                        for cmd in commands:
                            emit('cargo_start', level=level, branch=branch, command=' '.join(cmd), completed=report['cargo_checked'], total=360)
                            started = time.monotonic()
                            # Windows antivirus/indexing can transiently deny Cargo's
                            # creation of target/. Retry only this infrastructure error.
                            attempts = 0
                            while True:
                                attempts += 1
                                try:
                                    result = subprocess.run(cmd, cwd=target, capture_output=True,
                                                            text=True, timeout=180)
                                    code, stdout, stderr = result.returncode, result.stdout, result.stderr
                                except subprocess.TimeoutExpired as exc:
                                    code, stdout, stderr = 124, str(exc.stdout or ''), str(exc.stderr or '')
                                    stderr += '\nCommand timed out after 180 seconds'
                                except OSError as exc:
                                    code, stdout, stderr = 1, '', str(exc)
                                transient = (code != 0 and
                                             ('os error 5' in stderr.lower() or
                                              'access is denied' in stderr.lower() or
                                              'accès refusé' in stderr.lower()))
                                if not transient or attempts >= 3:
                                    break
                                emit('cargo_retry', level=level, branch=branch,
                                     command=' '.join(cmd), attempt=attempts,
                                     reason='transient access denied')
                                time.sleep(attempts * 2)

                            report['cargo_checked'] += 1
                            report['cargo_results'].append({
                                'branch': branch, 'command': ' '.join(cmd),
                                'exit_code': code, 'seconds': round(time.monotonic()-started, 2), 'attempts': attempts
                            })
                            emit('cargo_done', level=level, branch=branch, command=' '.join(cmd), exit_code=code, seconds=round(time.monotonic()-started, 2), completed=report['cargo_checked'], total=360)
                            if code:
                                report['cargo_failures'].append({
                                    'branch': branch, 'command': ' '.join(cmd),
                                    'exit_code': code,
                                    'stdout': stdout[-1500:], 'stderr': stderr[-2500:],
                                })
                    finally:
                        git(repo, 'worktree', 'remove', '--force', str(target))
    emit('audit_scans_done', total_levels=120, cargo_checked=report['cargo_checked'])
    report['cargo_verified'] = cargo and report['cargo_checked'] == 360 and not report['cargo_failures']
    report['ok'] = not any(report[key] for key in (
        'missing_branches', 'invalid_branches', 'content_failures', 'cargo_failures'
    )) and (not cargo or report['cargo_verified'])
    report['status'] = 'rust_verified' if report['ok'] and report['cargo_verified'] else (
        'structure_only' if report['ok'] else 'failed'
    )
    emit('audit_done', status=report['status'], cargo_checked=report['cargo_checked'], failures=len(report['cargo_failures']))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit all Rust RPG level branches')
    parser.add_argument('repository', type=Path)
    parser.add_argument('--cargo', action='store_true', help='Compile, lint and test every solution')
    parser.add_argument('--report', type=Path, default=Path('rust-rpg-audit.json'))
    args = parser.parse_args()
    result = audit(args.repository.resolve(), args.cargo)
    args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"Audit {result['status']}; Cargo checks: {result['cargo_checked']}; report: {args.report}")
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
