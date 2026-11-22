#!/usr/bin/env python3
"""Verbose, fail-closed Rust RPG release certification with live progress and logs."""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from audit import audit

HERE = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description='Certify Rust RPG with live progress')
    parser.add_argument('--report', type=Path, default=Path('rust-rpg-release-report.json'))
    parser.add_argument('--log', type=Path, default=Path('rust-rpg-release-check.log'))
    parser.add_argument('--heartbeat', type=int, default=10, help='Seconds between heartbeat updates (default: 10)')
    args = parser.parse_args()
    if args.heartbeat < 1:
        parser.error('--heartbeat must be at least 1')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger('rust-rpg-release')
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    file_handler = logging.FileHandler(args.log, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(message)s'))
    logger.addHandler(file_handler)
    start = time.monotonic()

    def show(message: str, *, error: bool = False) -> None:
        elapsed = time.monotonic() - start
        line = f'[{elapsed:7.1f}s] {message}'
        print(line, file=sys.stderr if error else sys.stdout, flush=True)
        (logger.error if error else logger.info)(message)

    def run_live(command: list[str], cwd: Path, title: str) -> tuple[int, str]:
        show(f'▶ {title}: {" ".join(command)}')
        output: list[str] = []
        with subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, errors='replace',
                              bufsize=1) as process:
            assert process.stdout is not None
            def reader() -> None:
                for line in process.stdout:
                    line = line.rstrip('\r\n')
                    output.append(line)
                    logger.info('  %s', line)
                    if line.strip():
                        print('    ' + line, flush=True)
            thread = threading.Thread(target=reader, daemon=True)
            thread.start()
            while process.poll() is None:
                thread.join(timeout=args.heartbeat)
                if process.poll() is None:
                    show(f'… {title} still running ({time.monotonic()-start:.0f}s elapsed overall)')
            thread.join()
            code = process.wait()
        show(f'{"✓" if code == 0 else "✗"} {title}: exit {code}', error=code != 0)
        return code, '\n'.join(output)

    result = {'python_tests': False, 'generation': False,
              'cargo_available': bool(shutil.which('cargo')),
              'rust_verified': False, 'status': 'failed'}
    show('🦀 RUST RPG RELEASE CERTIFICATION — START')
    show(f'Report: {args.report.resolve()} | Log: {args.log.resolve()}')
    show('Phases: 1/3 Python tests → 2/3 Git generation → 3/3 Cargo audit (360 checks)')
    try:
        show('PHASE 1/3 — Running Python unit tests')
        code, output = run_live([sys.executable, '-m', 'unittest', 'discover',
                                 '-s', str(HERE), '-p', 'test*.py', '-v'], HERE, 'Python tests')
        result['python_tests'] = code == 0
        result['python_test_output'] = output[-3000:]
        if code:
            result['reason'] = 'Python tests failed'
            return 1

        with tempfile.TemporaryDirectory(prefix='rust-rpg-release-') as directory:
            show('PHASE 2/3 — Generating 120 levels and 241 Git branches')
            command = [sys.executable, str(HERE / 'scaffold.py'), '--name', 'player',
                       '--output', directory, '--no-pause', '--quiet', '--no-sound',
                       '--skip-cargo-validation']
            code, output = run_live(command, HERE, 'Scaffold generation')
            result['generation'] = code == 0
            if code:
                result['generation_error'] = output[-3000:]
                result['reason'] = 'Scaffold generation failed'
                return 1
            if not result['cargo_available']:
                show('Cargo was not found on PATH; certification cannot continue', error=True)
                result['reason'] = 'Cargo missing: structural tests cannot certify Rust'
                return 1

            show('PHASE 3/3 — Auditing all 120 Rust solutions (fmt, clippy, test)')
            failures = 0
            def progress(event: str, **data) -> None:
                nonlocal failures
                if event == 'level_start':
                    show(f'LEVEL {data["level"]:03d}/120 — structural inspection')
                elif event == 'cargo_start':
                    show(f'  [{data["completed"]+1:03d}/360] START {data["branch"]}: {data["command"]}')
                elif event == 'cargo_retry':
                    show(f'  RETRY {data["attempt"]}/2: {data["branch"]} — {data["reason"]}')
                elif event == 'cargo_done':
                    if data['exit_code']:
                        failures += 1
                    show(f'  [{data["completed"]:03d}/360] '
                         f'{"PASS" if not data["exit_code"] else "FAIL"} '
                         f'{data["command"]} ({data["seconds"]:.1f}s) '
                         f'| failures: {failures}', error=bool(data['exit_code']))
                elif event == 'audit_done':
                    show(f'Audit complete: {data["status"]}; '
                         f'{data["cargo_checked"]}/360 Cargo checks; '
                         f'{data["failures"]} failures')
            audited = audit(Path(directory) / 'player', cargo=True, progress=progress)
            result['audit'] = audited
            result['rust_verified'] = audited['status'] == 'rust_verified'
            result['status'] = 'rust_verified' if result['rust_verified'] else 'failed'
            return 0 if result['rust_verified'] else 1
    except (OSError, RuntimeError, ValueError) as exc:
        result['reason'] = str(exc)
        show(f'ERROR: {exc}', error=True)
        return 1
    finally:
        result['elapsed_seconds'] = round(time.monotonic() - start, 2)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        show(f'RELEASE STATUS: {result["status"]} | elapsed {result["elapsed_seconds"]}s')
        show(f'JSON report: {args.report.resolve()}')
        show(f'Detailed log: {args.log.resolve()}')
        for handler in logger.handlers[:]:
            handler.flush()
            handler.close()
            logger.removeHandler(handler)


if __name__ == '__main__':
    raise SystemExit(main())
