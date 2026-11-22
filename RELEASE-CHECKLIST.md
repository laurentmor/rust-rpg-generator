# Rust RPG v1.0.0 release candidate — acceptance checklist

## Automated evidence (completed on Windows)

The supplied `release-report(3).json` reports 24 passing Python tests, 120 levels,
no missing or invalid branches, and **360/360 successful** Cargo checks (`fmt`,
`clippy -D warnings`, `test`). These results apply to the **v0.12.4** generator
archive and Rust toolchain used for that run; they do not prove future Rust
versions or other platforms.

Run `python -m unittest discover -s . -p 'test*.py' -v` to check the generator.
To validate a certification report against every expected branch and command,
run `python prepare_release.py --report release-report.json --artifact rust-rpg-kit-v1.0.0-rc1.zip --output release-manifest.json`.

## Manual installation smoke test (pending)

On a Windows machine with Python 3.11+, Git and Cargo on PATH, extract the kit
into a **fresh** directory and run:

```powershell
python scaffold.py FR --name rust-rpg-fr-smoke --output . --no-pause --no-sound
cd rust-rpg-fr-smoke
git branch --list | Measure-Object -Line
git switch level-001/work
cargo test --workspace
git switch level-001/solutions
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
git switch main
```

The `work` branch may intentionally fail its tests; this is expected gameplay.
Check that `README.md`, `MASTER_PROMPT.md`, `LEVEL.md` and boss instructions
are readable, that instructions are in French, and that solutions were **not**
published to a remote. Check `git branch --list` contains 241 branches.

Repeat an English-language install with `python scaffold.py EN --name rust-rpg-en-smoke --output . --no-pause --no-sound` and inspect its docs.

## Security and release hygiene

- Do not publish `*/solutions` branches without explicit authorization.
- Do not include private credentials, temporary repositories, or `target/` build outputs.
- Record the Git and Cargo versions, Windows version, smoke-test results and date.
- Attach the original JSON report and the generated SHA-256 manifest to the release.
- Mark **v1.0.0 stable** only after manual bilingual smoke tests pass. Until then, use **v1.0.0-rc1**.
