# Rust RPG — The Ownership Chronicles (generator kit)

A Python 3.11+ scaffolding kit for a bilingual, Git-native Rust learning campaign with 120 levels, 12 chapters, and 240 per-level work/solutions branches.

## Requirements

- Python 3.11+
- Git
- Rust toolchain with `cargo`, `rustfmt`, `clippy` (for validated generation)

## Generate a player repository

```bash
python scaffold.py --name rust-rpg-player
python scaffold.py FR --name rust-rpg-joueur
```

The generated repository contains `README.md` and `MASTER_PROMPT.md`, 120 `LEVEL.md` briefs (one per branch), testable Rust starter code and reference solutions, Git hooks, a GitHub Actions workflow, and `publish.py`.

## Publish

Create an empty repository on GitHub. In the generated player repository:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
python publish.py --remote origin
# Explicit opt-in to publishing solutions:
python publish.py --remote origin --solutions
```

**Never run `git push --all` if you intend to keep solutions private.**

## Tests

```bash
python -m unittest discover -v
```

## Important scope disclosure

This is a **curriculum-in-progress release**, not a complete expert curriculum. The catalog now contains **120 different Rust functions**, each with its own API, reference implementation, and acceptance assertions. The first 30 levels cover foundations, ownership and modeling with varied exercises. Levels 81–110 now include 30 topic-specific standard-library labs: actual threads, channels, locks, loopback TCP, manual future polling, macros, unsafe pointers, C FFI, Pin, and interior mutability. These are focused exercises, not yet large integrated projects. Levels 31–80 and 111–120 still need deeper topic-specific work, and Tokio/Serde/HTTP frameworks are not yet implemented. Some labs require loopback sockets or a platform C runtime. Rust compilation was not available in the build environment, so all solutions must be validated on a Rust-equipped machine.

Generation is intentionally fail-fast and does not silently publish any branches. `--skip-cargo-validation` is provided for generator development only, not for normal usage. The default generator validates reference solutions with Cargo, Clippy and tests before completion.

## Interactive installer (v0.3)

The scaffolder displays a colored introduction, explains its actions, prints a progress bar for each of the 120 levels (including the chapter and level topic), and plays short terminal sounds when supported. A keyboard-only start/quit menu confirms generation, estimated time remaining is displayed during Git generation, and Cargo validation has its own progress indicator. Interrupted scaffolding can be resumed using `--resume` (completed branches are preserved). In an interactive terminal, it waits for **Enter** before closing. Use `FR` to select French output and game text.

```bash
python scaffold.py --name my-rust-rpg
python scaffold.py FR --name mon-rust-rpg
python scaffold.py FR --no-sound
python scaffold.py FR --name mon-rust-rpg --resume
python scaffold.py --no-pause --quiet  # automation / CI
```

A complete UTF-8 execution log is written to `<repository-name>-scaffold.log` beside the generated repository, including every Git/Cargo command, stdout, stderr, and exit status. It is stored outside the Git repository to avoid accidental publication. Terminal colors/sounds require an interactive terminal; noninteractive execution retains plain progress messages and logs. Cargo validation is mandatory by default; `--skip-cargo-validation` is for scaffolder testing only.

## After installation: start playing

The installer displays these steps at completion in the selected language:

```bash
cd rust-rpg-player
git switch level-001/work
# Read LEVEL.md and edit src/lib.rs
cargo fmt
cargo clippy --all-targets -- -D warnings
cargo test
git add .
git commit -m "feat(level-001): complete first quest"
```

Read `README.md` and paste `MASTER_PROMPT.md` into ChatGPT to start the mentor session. Continue to `level-002/work` only after mentor approval. The complete terminal session and Git/Cargo command results are logged to the `.log` file next to the repository.

## Advanced integration labs (v0.5)

Levels **081–090** exercise actual concurrency primitives (`thread`, `mpsc`, `Arc`, `Mutex`, `RwLock`, `Send + Sync`) including a multiworker boss. Levels **091–100** cover `Future`, `Pin`, `Poll`, `Waker`, TCP loopback, HTTP framing, and cancellation; they **do not claim to implement Tokio or an async runtime**. Levels **101–110** include `macro_rules!`, documented unsafe pointer operations, C ABI calls, `RefCell`, profiling, and a macro/unsafe boss.

The new labs are compiled only when a local Rust toolchain is present. The Python generator tests verify catalog structure and branch content, not Rust correctness. Default scaffolding runs Cargo validation and fails if the solutions do not compile.

## v0.6 applied labs

Levels **71–80** now include real standard-library path and file operations,
buffered input, restricted CSV handling, JSON/XML string escaping, CLI parsing,
structured records, and a fallible data pipeline. These are deliberately scoped
exercises, **not** substitutes for production Serde/XML crates.

Levels **111–120** now include command parsing, typed records, error taxonomy,
file persistence, worker pipelines, metrics, identifier validation, release
version parsing, and an aggregation checkpoint. The final checkpoint is not yet
a full multi-crate capstone. All 20 new quests remain dependency-free and can
be generated offline. Cargo compilation is still required before treating
solutions as verified.


## v0.7 — Core Rust labs

Levels 31–50 now cover fallible operations, contextual errors, checked arithmetic, genuine generic type parameters, trait bounds, explicit lifetimes and trait objects. Levels 61–70 add engineering-oriented exercises, including workspace paths, environment configuration and restricted version parsing. Levels 51–60 retain their existing iterator/closure exercises.

**Validation status:** Python generator tests pass; Rust compilation and Clippy have **not** been executed in this environment. Run the scaffold with Cargo validation enabled on a Rust-equipped computer. The complete multi-crate final capstone remains outstanding.

## v0.8: multi-crate final capstone (level 120)

Level 120 now contains a real two-crate Cargo workspace (`rpg-core`, `rpg-cli`),
with an executable, filesystem-based end-to-end tests, line-numbered parsing
errors and checked aggregation. The work branch exposes stubs; the solution
branch contains the reference implementation. This capstone intentionally uses
only the standard library and a restricted CSV dialect; it is not a complete
production-grade processing service. The other boss levels remain standalone
exercises. Rust compilation must be verified on a machine with Cargo.

## v0.9 — Boss integration reviews and repository audit

Each chapter boss (levels 010, 020, …, 120) now includes an explicit integration challenge, edge cases, and a game-master oral review rubric in `LEVEL.md`. The coding kata is still separate from the full integration challenge: the latter is a guided assignment, not a fully automated multi-crate implementation.

Audit all branches without requiring Rust:

```bash
python audit.py ./rust-rpg --report audit.json
```

Validate all 120 reference branches with a local Rust toolchain:

```bash
python audit.py ./rust-rpg --cargo --report cargo-audit.json
```

The audit refuses dirty worktrees, returns a nonzero exit status on detected failures, and writes a machine-readable JSON report. This command switches branches and should not be run while editing the player repository.

## Release readiness audit (v0.10)

The read-only structural audit checks all 240 level branches without switching the
player's current branch or discarding uncommitted changes:

```bash
python audit.py ./rust-rpg-player --report rust-rpg-audit.json
```

For an actual Rust release gate, install the stable Rust toolchain with rustfmt and
Clippy and run:

```bash
python audit.py ./rust-rpg-player --cargo --report rust-rpg-cargo-audit.json
```

This runs **360 Cargo checks** (format, Clippy and tests on each of 120 solution
branches) in temporary detached Git worktrees. It does not alter the player's
working tree. It requires sufficient disk space and may take considerable time.
The JSON `status` distinguishes `structure_only` from `rust_verified` and
`failed`; **`structure_only` does not mean that Rust compiles**. Missing Cargo
with `--cargo` is a hard failure. Review every failed branch and fix its source
in the generator before regenerating player repositories.

**v1.0 release gate:** 360/360 Cargo checks, fully implemented and independently
tested boss challenges, and a smoke test of interactive setup on Windows.

## v0.11 — Remote Rust verification (opt-in)

The generated player repository now includes `audit.py` and an additional
**manually triggered** GitHub Actions workflow, `audit-solutions.yml`. It
fetches all published level branches, runs `cargo fmt --check`, Clippy and
Cargo tests against each of the 120 solution branches in isolated Git worktrees,
and uploads a JSON evidence report even when verification fails.

**Solutions remain local by default.** To run the remote audit, first publish
solution branches explicitly (`python publish.py --remote origin --solutions`),
then start **Actions → Audit all Rust RPG solutions → Run workflow**.
Publishing solution branches makes their contents visible to anyone with access
to that GitHub repository. Use a private repository for instructor-only audits.

The audit records each Cargo command's exit status and duration, and times out
individual commands after 180 seconds. This release does **not** claim that
all solutions compile: that requires executing the audit on a Rust-equipped
machine or GitHub runner and reviewing the JSON report. Existing v0.10 player
repositories must be regenerated to receive the new workflow.

## v0.12 — Executable boss labs and acceptance gates

Boss levels **010–110** now generate an additional `src/boss.rs` module containing a
chapter integration challenge, a solution (on the solutions branch), and executable
acceptance tests. Boss 120 retains the multi-crate capstone. Both the ordinary kata
and the boss lab must pass `cargo test`. The independent auditor now rejects branches
that omit the executable boss or its tests. The game master still assesses conceptual
understanding and alternative valid solutions.

**Verification limitation:** Python tests and structural Git audits do not certify Rust
compilation. This kit must not be called Rust-verified until a complete `audit.py
--cargo` run returns `status: rust_verified`. The current release has not achieved
that certification. The GitHub workflow provides an opt-in path to run it.

### One-command release gate

```bash
python release_check.py --report release-report.json
```

This command runs the Python suite, generates a clean 241-branch repository,
then checks all 120 reference solutions with Cargo. It exits nonzero if Rust
is unavailable or **any** validation fails. Never label a release stable based
on the structural audit alone.

## Verbose release certification (v0.12.1)

The release gate now streams Python test and scaffolding output immediately,
prints a heartbeat while long commands are running, and displays each level and
Cargo validation (`fmt`, `clippy`, `test`) with its result and duration. A
full timestamped log and a JSON report are written even if certification fails.

```bash
python -u release_check.py --report release-report.json --log release-check.log
```

Use `--heartbeat 5` to print an activity reminder every five seconds during
long-running subprocesses. The release gate requires Cargo on PATH and will
fail closed if Rust validation cannot be performed.

## Release validation fix (v0.12.2)

The generator now runs `cargo fmt --all` on every generated level branch **before** committing
its contents, provided Cargo is available. This also formats starter (`work`) branches.
Known Clippy findings from the Windows Cargo 1.99.0 report were addressed: levels 001 and
053 use idiomatic implementations, while levels 020, 026, 048 and 101 use narrowly scoped
lint allowances to retain the intended teaching examples.

Generate a **new repository** to receive these fixes; existing branches are not rewritten by
`--resume`. Run `python -u release_check.py --report release-report.json --log release-check.log`
and inspect its result before publishing. This package has not been fully Cargo-certified in
this build environment.

## v1.0.0-rc1 — Release candidate

The v0.12.4 generator passed a full 360/360 Cargo audit on the user's Windows
machine. This release candidate adds `prepare_release.py`, a strict evidence
validator, SHA-256 release manifest generation and `RELEASE-CHECKLIST.md` for
bilingual installation and gameplay smoke testing. **Manual smoke testing is
still pending; this is not yet v1.0.0 stable.**
