"""Offline, multi-crate level 120 capstone: event processing CLI."""
from pathlib import Path

CORE_SOL = '''use std::fmt;
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Record { pub id: String, pub value: i64 }
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError { InvalidFormat(usize), InvalidId(usize), InvalidNumber(usize), Overflow }
impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "{self:?}") }
}
impl std::error::Error for ParseError {}
pub fn parse(input: &str) -> Result<Vec<Record>, ParseError> {
    input.lines().enumerate().filter(|(_, line)| !line.trim().is_empty())
        .map(|(index, line)| {
            let number = index + 1;
            let (id, value) = line.split_once(',').ok_or(ParseError::InvalidFormat(number))?;
            if id.is_empty() || !id.bytes().all(|c| c.is_ascii_alphanumeric() || c == b'_' || c == b'-') {
                return Err(ParseError::InvalidId(number));
            }
            let value = value.trim().parse::<i64>().map_err(|_| ParseError::InvalidNumber(number))?;
            Ok(Record { id: id.to_owned(), value })
        }).collect()
}
pub fn summarize(records: &[Record]) -> Result<(usize, i64), ParseError> {
    let total = records.iter().try_fold(0_i64, |sum, record| sum.checked_add(record.value).ok_or(ParseError::Overflow))?;
    Ok((records.len(), total))
}
'''
CORE_WORK = '''use std::fmt;
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Record { pub id: String, pub value: i64 }
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ParseError { InvalidFormat(usize), InvalidId(usize), InvalidNumber(usize), Overflow }
impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "{self:?}") }
}
impl std::error::Error for ParseError {}
pub fn parse(_input: &str) -> Result<Vec<Record>, ParseError> { todo!("Implement parser") }
pub fn summarize(_records: &[Record]) -> Result<(usize, i64), ParseError> { todo!("Implement checked aggregation") }
'''
CLI_SOL = '''use std::error::Error;
use std::path::Path;
pub fn run(path: &Path) -> Result<String, Box<dyn Error>> {
    let content = std::fs::read_to_string(path)?;
    let records = rpg_core::parse(&content)?;
    let (count, total) = rpg_core::summarize(&records)?;
    Ok(format!("records={count};total={total}"))
}
'''
CLI_WORK = '''use std::error::Error;
use std::path::Path;
pub fn run(_path: &Path) -> Result<String, Box<dyn Error>> { todo!("Connect file input, parser and summary") }
'''
MAIN = '''fn main() {
    let Some(path) = std::env::args_os().nth(1) else {
        eprintln!("usage: rpg-cli <input.csv>");
        std::process::exit(2);
    };
    match rpg_cli::run(std::path::Path::new(&path)) {
        Ok(report) => println!("{report}"),
        Err(error) => { eprintln!("error: {error}"); std::process::exit(1); }
    }
}
'''
TESTS = '''use rpg_core::{parse, summarize, ParseError};
#[test]
fn accepts_records_and_reports_checked_total() {
    let records = parse("a,2\\nb,-3\\n").unwrap();
    assert_eq!(records.len(), 2);
    assert_eq!(summarize(&records), Ok((2, -1)));
}
#[test]
fn rejects_malformed_records_and_unsafe_identifiers() {
    assert_eq!(parse("invalid"), Err(ParseError::InvalidFormat(1)));
    assert_eq!(parse("../bad,1"), Err(ParseError::InvalidId(1)));
    assert_eq!(parse("ok,NaN"), Err(ParseError::InvalidNumber(1)));
}
#[test]
fn detects_overflow() {
    let records = parse("a,9223372036854775807\\nb,1").unwrap();
    assert_eq!(summarize(&records), Err(ParseError::Overflow));
}
#[test]
fn end_to_end_file() {
    let path = std::env::temp_dir().join(format!("rpg-capstone-{}-{:?}.csv", std::process::id(), std::thread::current().id()));
    std::fs::write(&path, "alpha,3\\nbeta,4\\n").unwrap();
    let result = rpg_cli::run(&path);
    std::fs::remove_file(&path).unwrap();
    assert_eq!(result.unwrap(), "records=2;total=7");
}
'''

def create_capstone(root: Path, lang: str, solution: bool) -> None:
    def write(name: str, content: str) -> None:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    write('Cargo.toml', '[workspace]\nmembers = ["crates/rpg-core", "crates/rpg-cli"]\nresolver = "2"\n')
    write('crates/rpg-core/Cargo.toml', '[package]\nname = "rpg-core"\nversion = "0.1.0"\nedition = "2021"\n')
    write('crates/rpg-cli/Cargo.toml', '[package]\nname = "rpg-cli"\nversion = "0.1.0"\nedition = "2021"\n[dependencies]\nrpg-core = { path = "../rpg-core" }\n')
    write('crates/rpg-core/src/lib.rs', CORE_SOL if solution else CORE_WORK)
    write('crates/rpg-cli/src/lib.rs', CLI_SOL if solution else CLI_WORK)
    write('crates/rpg-cli/src/main.rs', MAIN)
    write('crates/rpg-cli/tests/pipeline.rs', TESTS)
    if lang == 'FR':
        instructions = '''# Niveau 120 — Projet final multi-crates

**Objectif :** intégrer les concepts Rust dans un workspace Cargo.

Construis un processeur de fichiers CSV simplifié, sans dépendances externes.

- `rpg-core`: analyser les lignes `identifiant,nombre`, valider les identifiants et les erreurs numérotées par ligne, calculer une somme avec détection des débordements.
- `rpg-cli`: lire un fichier UTF-8, appeler le cœur et produire `records=N;total=S`.
- Le binaire doit accepter un chemin et retourner un code non nul en cas d'erreur.
- Les tests d'intégration sont fournis. Ne consulte pas la branche de solutions.

Validation : `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`.

Limites : CSV volontairement restreint (pas de champs entre guillemets), aucune garantie de persistance atomique, pas d'async ni de réseau. Explique ces compromis au professeur.
'''
    else:
        instructions = '''# Level 120 — Multi-crate final capstone

Build a dependency-free, restricted-CSV file processor.

- `rpg-core`: parse `identifier,number` records, reject unsafe IDs, return line-numbered errors, aggregate with checked overflow.
- `rpg-cli`: read a UTF-8 file, invoke the core and report `records=N;total=S`.
- The executable accepts a file path and returns nonzero on failure.
- Integration tests are provided. Do not inspect the solutions branch.

Validation: `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`.

Scope: intentionally restricted CSV (no quoted fields); no atomic persistence, async runtime, or network. Explain these trade-offs to your instructor.
'''
    write('LEVEL.md', instructions)
