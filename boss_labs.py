"""Executable integration challenges for boss levels 10..110.

Each boss adds an independently tested public API to the level's existing kata.
No external crates are needed. Reference solutions are intentionally small enough
for an instructor to review, but combine multiple chapter concepts.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class BossLab:
    brief: str
    signature: str
    solution: str
    tests: str

BOSS_LABS = {
10: BossLab('Parse comma-separated character scores; reject invalid or out-of-range entries, then sum safely.',
 'pub fn character_score(input: &str) -> Result<u32, String>',
 '''let mut total = 0u32;
    if input.trim().is_empty() { return Err("empty scores".into()); }
    for field in input.split(',') {
        let score: u32 = field.trim().parse().map_err(|_| "invalid score".to_string())?;
        if score > 100 { return Err("score exceeds 100".into()); }
        total = total.checked_add(score).ok_or("total overflow")?;
    }
    Ok(total)''',
 'assert_eq!(character_score("10, 20,30"), Ok(60)); assert!(character_score("").is_err()); assert!(character_score("101").is_err()); assert!(character_score("a").is_err());'),
20: BossLab('Return borrowed words longer than a character threshold without cloning their contents.',
 "pub fn long_words(text: &str, min_chars: usize) -> Vec<&str>",
 'text.split_whitespace().filter(|word| word.chars().count() > min_chars).collect()',
 'assert_eq!(long_words("école rust chat", 4), vec!["école"]); assert!(long_words("", 2).is_empty());'),
30: BossLab('Apply a typed event stream to a registry; reject duplicate creates and updates of missing IDs.',
 'pub fn apply_events(events: &[Event]) -> Result<std::collections::HashMap<u32, String>, String>',
 '''let mut state = std::collections::HashMap::new();
    for event in events {
        match event {
            Event::Create(id, value) => {
                if state.insert(*id, value.clone()).is_some() { return Err("duplicate id".into()); }
            }
            Event::Update(id, value) => {
                let existing = state.get_mut(id).ok_or("missing id")?;
                *existing = value.clone();
            }
            Event::Delete(id) => {
                if state.remove(id).is_none() { return Err("missing id".into()); }
            }
        }
    }
    Ok(state)''',
 'let events = [Event::Create(1, "a".into()), Event::Update(1, "b".into())]; assert_eq!(apply_events(&events).unwrap().get(&1).map(String::as_str), Some("b")); assert!(apply_events(&[Event::Delete(9)]).is_err()); assert!(apply_events(&[Event::Create(1,"a".into()), Event::Create(1,"b".into())]).is_err());'),
40: BossLab('Import newline-separated signed integers, attach line numbers to parse failures and detect overflow.',
 'pub fn import_total(input: &str) -> Result<i64, String>',
 '''let mut sum = 0i64;
    for (index, line) in input.lines().enumerate() {
        let value: i64 = line.trim().parse().map_err(|_| format!("line {}: invalid integer", index + 1))?;
        sum = sum.checked_add(value).ok_or_else(|| format!("line {}: overflow", index + 1))?;
    }
    Ok(sum)''',
 'assert_eq!(import_total("1\\n-2\\n3"), Ok(2)); assert_eq!(import_total(""), Ok(0)); assert!(import_total("1\\noops").unwrap_err().contains("line 2")); assert!(import_total("9223372036854775807\\n1").is_err());'),
50: BossLab('Find the highest-ranked borrowed item using generic ordering; return None on empty input.',
 "pub fn top_ranked<T: Ord>(items: &[T]) -> Option<&T>",
 'items.iter().max()',
 'assert_eq!(top_ranked(&[2, 8, 4]), Some(&8)); assert_eq!(top_ranked(&["a", "z"]), Some(&"z")); assert_eq!(top_ranked::<i32>(&[]), None);'),
60: BossLab('Build a lazy iterator pipeline that filters positive even integers, squares them and returns their sum.',
 'pub fn filtered_square_sum(values: &[i32]) -> i64',
 'values.iter().copied().filter(|x| *x > 0 && x % 2 == 0).map(|x| i64::from(x) * i64::from(x)).sum()',
 'assert_eq!(filtered_square_sum(&[-2, 1, 2, 4]), 20); assert_eq!(filtered_square_sum(&[]), 0);'),
70: BossLab('Normalize relative workspace paths, rejecting absolute paths and parent traversal.',
 'pub fn safe_member_path(path: &str) -> Result<String, String>',
 '''use std::path::Component;
    let path = std::path::Path::new(path);
    let mut parts = Vec::new();
    for component in path.components() {
        match component {
            Component::Normal(part) => parts.push(part.to_string_lossy().into_owned()),
            Component::CurDir => {},
            _ => return Err("unsafe path".into()),
        }
    }
    if parts.is_empty() { return Err("empty path".into()); }
    Ok(parts.join("/"))''',
 'assert_eq!(safe_member_path("./crates/core"), Ok("crates/core".into())); assert!(safe_member_path("../secret").is_err()); assert!(safe_member_path("/root").is_err());'),
80: BossLab('Read a text file, parse nonempty numeric lines and report line-specific errors.',
 'pub fn ingest_file(path: &std::path::Path) -> Result<Vec<i64>, String>',
 '''use std::io::{BufRead, BufReader};
    let file = std::fs::File::open(path).map_err(|e| e.to_string())?;
    BufReader::new(file).lines().enumerate().filter_map(|(i, line)| {
        match line {
            Ok(value) if value.trim().is_empty() => None,
            Ok(value) => Some(value.trim().parse::<i64>().map_err(|_| format!("line {}: invalid", i + 1))),
            Err(error) => Some(Err(error.to_string())),
        }
    }).collect()''',
 '''let path = std::env::temp_dir().join(format!("rust_rpg_boss_80_{}", std::process::id()));
        std::fs::write(&path, "1\\n\\n-3\\n").unwrap();
        assert_eq!(ingest_file(&path), Ok(vec![1, -3]));
        std::fs::write(&path, "1\\noops\\n").unwrap();
        assert!(ingest_file(&path).unwrap_err().contains("line 2"));
        std::fs::remove_file(path).unwrap();'''),
90: BossLab('Use worker threads and a channel to square inputs while restoring input order.',
 'pub fn parallel_squares(values: &[u32]) -> Vec<u64>',
 '''use std::sync::mpsc;
    let (tx, rx) = mpsc::channel();
    let mut handles = Vec::new();
    for (index, &value) in values.iter().enumerate() {
        let sender = tx.clone();
        handles.push(std::thread::spawn(move || {
            sender.send((index, u64::from(value) * u64::from(value))).expect("receiver alive");
        }));
    }
    drop(tx);
    let mut results = vec![0; values.len()];
    for (index, result) in rx { results[index] = result; }
    for handle in handles { handle.join().expect("worker panicked"); }
    results''',
 'assert_eq!(parallel_squares(&[3, 1, 2]), vec![9, 1, 4]); assert!(parallel_squares(&[]).is_empty());'),
100: BossLab('Read a TCP stream until newline with a maximum frame length; reject oversized or disconnected frames.',
 'pub fn read_frame(stream: &mut std::net::TcpStream, max: usize) -> std::io::Result<Vec<u8>>',
 '''use std::io::{Error, ErrorKind, Read};
    let mut frame = Vec::new();
    loop {
        let mut byte = [0u8; 1];
        if stream.read(&mut byte)? == 0 { return Err(Error::new(ErrorKind::UnexpectedEof, "incomplete frame")); }
        if byte[0] == b'\\n' { return Ok(frame); }
        if frame.len() >= max { return Err(Error::new(ErrorKind::InvalidData, "frame too long")); }
        frame.push(byte[0]);
    }''',
 '''use std::io::Write;
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let address = listener.local_addr().unwrap();
        let sender = std::thread::spawn(move || {
            let mut stream = std::net::TcpStream::connect(address).unwrap();
            stream.write_all(b"hi\\n").unwrap();
        });
        let (mut incoming, _) = listener.accept().unwrap();
        assert_eq!(read_frame(&mut incoming, 4).unwrap(), b"hi");
        sender.join().unwrap();'''),
110: BossLab('Expose a safe checked slice reader around a small audited unsafe pointer operation.',
 'pub fn checked_read(values: &[u32], index: usize) -> Option<u32>',
 '''if index >= values.len() { return None; }
    // SAFETY: index < values.len() was checked above, and the pointer originates
    // from a valid shared slice for the duration of this call.
    Some(unsafe { *values.as_ptr().add(index) })''',
 'assert_eq!(checked_read(&[5, 9], 1), Some(9)); assert_eq!(checked_read(&[5], 1), None); assert_eq!(checked_read(&[], 0), None);'),
}

EXTRA = {30: '#[derive(Debug, Clone)]\npub enum Event { Create(u32, String), Update(u32, String), Delete(u32) }\n\n'}

def render(level: int, solution: bool) -> str:
    lab = BOSS_LABS[level]
    body = lab.solution if solution else 'todo!("Complete the boss integration challenge")'
    return (f'//! Boss integration challenge for level {level:03d}.\n'
            + EXTRA.get(level, '')
            + f'/// {lab.brief}\n{lab.signature} {{\n    {body}\n}}\n'
            + f'\n#[cfg(test)]\nmod tests {{\n    use super::*;\n    #[test]\n    fn boss_acceptance() {{\n        {lab.tests}\n    }}\n}}\n')
