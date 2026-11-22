#!/usr/bin/env python3
"""Rust RPG repository generator. Python 3.11+, Git, Rust toolchain required."""
from __future__ import annotations
import argparse
import json
import logging
import time
import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import math
from quest_catalog import QUESTS
from integration_labs import INTEGRATION_QUESTS
from project_labs import PROJECT_QUESTS
from core_labs import CORE_QUESTS, GENERIC_SIGNATURES
from capstone import create_capstone
from boss_guides import guide as boss_guide
from boss_labs import BOSS_LABS, render as render_boss

CHAPTERS = [
 ('Foundations','Variables and bindings|Scalar types|Strings and UTF-8|Functions|Expressions and blocks|Conditionals|Loops|Ranges|Pattern basics|Foundation boss'),
 ('Ownership','Move semantics|Copy types|Immutable borrowing|Mutable borrowing|Borrow scopes|String slices|Array slices|Ownership in functions|Avoiding clones|Ownership boss'),
 ('Modeling','Struct definitions|Struct methods|Tuple structs|Enums|Option|Match expressions|If let|Vectors|Hash maps|Modeling boss'),
 ('Errors and Testing','Result|Propagation with question mark|Custom errors|Unit tests|Integration tests|Table driven tests|Assertions|Error context|Test organization|Reliability boss'),
 ('Generics and Traits','Generic functions|Generic structs|Trait definitions|Trait implementations|Trait bounds|Default methods|Associated types|Lifetimes|Trait objects|Abstraction boss'),
 ('Functional Rust','Closures|Fn traits|Iterator basics|Map and filter|Collect|Fold|Iterator ownership|Custom iterators|Combinators|Iterator boss'),
 ('Engineering','Modules|Visibility|Crate organization|Cargo features|Workspaces|Documentation tests|Dependency hygiene|Configuration|Semantic versioning|Engineering boss'),
 ('Files and Data','Paths|File reading|File writing|Buffered I O|CSV parsing|Serde JSON|XML processing|CLI arguments|Structured logging|Data pipeline boss'),
 ('Concurrency','Threads|Move closures|Channels|Mutex|Arc|RwLock|Send and Sync|Thread errors|Parallel work|Concurrency boss'),
 ('Async and Networking','Async functions|Futures|Tokio runtime|Async tasks|Async channels|TCP basics|HTTP client|HTTP server|Cancellation|Networking boss'),
 ('Advanced Rust','Declarative macros|Macro patterns|Unsafe blocks|Raw pointers|FFI boundaries|Pin concepts|Interior mutability|Performance profiling|Zero cost abstractions|Advanced boss'),
 ('Master Challenges','CLI architecture|Parser design|Error taxonomy|Persistence layer|Concurrent pipeline|Async integration|Observability|Security review|Release engineering|Final capstone'),
]
assert len(CHAPTERS)==12 and all(len(s.split('|'))==10 for _,s in CHAPTERS)

EN = {'title':'Rust RPG — The Ownership Chronicles','mission':'Mission','objective':'Objective','task':'Implement the function described below. Preserve the public API and pass the tests.','rule':'Do not inspect the solutions branch before completing your own attempt.','boss':'Boss battle','work':'Work branch','solution':'Reference solution','next':'Next step','note':'Each level is an independent, focused exercise; later levels introduce larger engineering challenges.'}
FR = {'title':'Rust RPG — Les Chroniques de l’Ownership','mission':'Mission','objective':'Objectif','task':'Implémente la fonction décrite ci-dessous. Préserve l’API publique et réussis les tests.','rule':'Ne consulte pas la branche de solutions avant d’avoir terminé ton essai.','boss':'Combat de boss','work':'Branche de travail','solution':'Solution de référence','next':'Prochaine étape','note':'Chaque niveau est un exercice ciblé indépendant ; les niveaux avancés introduisent des défis d’ingénierie plus vastes.'}

# The exercise family changes every ten levels. Each instance has a unique target and tests.
def exercise(n:int):
    chapter=(n-1)//10
    k=(n-1)%10+1
    if chapter==0:
        return ('sum_to', 'limit: u32', 'u32','(1..=limit).sum()',f'{(k+2)*(k+3)//2}',f'Sum the integers from 1 through {k+2} (inclusive).',f'additionner les entiers de 1 à {k+2} inclus')
    if chapter==1:
        return ('borrowed_length', 'input: &str', 'usize', 'input.chars().count()',str(k+2),f'Count Unicode scalar values in a borrowed string. Test input: {"a"*(k+2)}.',f'Compter les valeurs scalaires Unicode d’une chaîne empruntée. Entrée : {"a"*(k+2)}')
    if chapter==2:
        return ('classify', 'value: i32', "&'static str",'if value < 0 { "negative" } else if value == 0 { "zero" } else { "positive" }','"positive"',f'Classify the integer {k} as negative, zero, or positive.',f'Classifier l’entier {k} : négatif, zéro ou positif')
    if chapter==3:
        return ('checked_divide','a: i32, b: i32','Result<i32, String>','a.checked_div(b).ok_or_else(|| "division failed".to_string())',f'Ok({k})',f'Divide {k*2} by 2 safely; return an error on zero divisor or overflow.',f'Diviser {k*2} par 2 de manière sûre ; erreur si division par zéro ou débordement')
    if chapter==4:
        return ('largest','values: &[i32]','Option<i32>','values.iter().copied().max()',f'Some({k+1})',f'Find the largest value in a borrowed slice, or None when empty.',f'Trouver la plus grande valeur d’une tranche empruntée, ou None si vide')
    if chapter==5:
        return ('even_squares','values: &[i32]','Vec<i32>','values.iter().filter(|v| **v % 2 == 0).map(|v| v * v).collect()',f'vec![4, 16]',f'Use iterators to square even numbers without modifying the input.',f'Utiliser des itérateurs pour mettre au carré les nombres pairs sans modifier l’entrée')
    if chapter==6:
        return ('slugify','input: &str','String','input.trim().to_lowercase().split_whitespace().collect::<Vec<_>>().join("-")','"rust-rpg".to_string()',f'Convert whitespace-separated words into a lowercase hyphenated slug.',f'Convertir des mots séparés par des espaces en identifiant minuscule avec traits d’union')
    if chapter==7:
        return ('line_count','input: &str','usize','input.lines().count()',str(k),f'Count logical lines in text (including non-terminated final line).',f'Compter les lignes logiques d’un texte, y compris la dernière sans saut de ligne')
    if chapter==8:
        return ('shared_total','values: &[u32]','u32','values.iter().sum()',str(k*3),f'Compute a total over data suitable for shared read-only access.',f'Calculer un total sur des données adaptées à un accès partagé en lecture seule')
    if chapter==9:
        return ('parse_port','input: &str','Result<u16, String>','input.parse::<u16>().map_err(|e| e.to_string())',f'Ok({8000+k})',f'Parse a valid TCP port number; reject invalid values.',f'Analyser un numéro de port TCP valide ; rejeter les valeurs invalides')
    if chapter==10:
        return ('clamp','value: i32, min: i32, max: i32','i32','value.clamp(min, max)',str(k),f'Clamp a number into an inclusive interval with min <= max.',f'Limiter un nombre à un intervalle inclusif où min <= max')
    return ('checksum','bytes: &[u8]','u32','bytes.iter().map(|b| u32::from(*b)).sum()',str(k*2),f'Calculate a simple byte checksum without overflowing u8.',f'Calculer une somme de contrôle simple des octets sans débordement u8')

def tests(n):
    chapter=(n-1)//10; k=(n-1)%10+1
    cases=[f'assert_eq!(sum_to(0), 0); assert_eq!(sum_to({k+2}), {(k+2)*(k+3)//2});',
           f'assert_eq!(borrowed_length("{"a"*(k+2)}"), {k+2}); assert_eq!(borrowed_length("é"), 1);',
           f'assert_eq!(classify({k}), "positive"); assert_eq!(classify(-1), "negative"); assert_eq!(classify(0), "zero");',
           f'assert_eq!(checked_divide({k*2}, 2), Ok({k})); assert!(checked_divide(1, 0).is_err()); assert!(checked_divide(i32::MIN, -1).is_err());',
           f'assert_eq!(largest(&[1, {k+1}, 0]), Some({k+1})); assert_eq!(largest(&[]), None);',
           'assert_eq!(even_squares(&[1,2,3,4]), vec![4,16]); assert!(even_squares(&[]).is_empty());',
           'assert_eq!(slugify(" Rust  RPG "), "rust-rpg"); assert_eq!(slugify(""), "");',
           f'assert_eq!(line_count(&{"""""" if False else repr(chr(10).join(["x"]*k))}), {k});',
           f'assert_eq!(shared_total(&[{k}, {k}, {k}]), {k*3}); assert_eq!(shared_total(&[]), 0);',
           f'assert_eq!(parse_port("{8000+k}"), Ok({8000+k})); assert!(parse_port("invalid").is_err());',
           f'assert_eq!(clamp({k}, 0, 20), {k}); assert_eq!(clamp(-1, 0, 20), 0);',
           f'assert_eq!(checksum(&[{k}, {k}]), {k*2}); assert_eq!(checksum(&[]), 0);']
    if chapter==7:
        cases[7]=f'assert_eq!(line_count({json.dumps(chr(10).join(["x"]*k))}), {k}); assert_eq!(line_count(""), 0);'
    return cases[chapter]

LOGGER = logging.getLogger('rust_rpg')

def run(cmd,cwd,check=True):
    LOGGER.info('COMMAND cwd=%s argv=%s', cwd, cmd)
    p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.stdout.strip(): LOGGER.info('STDOUT: %s',p.stdout.strip())
    if p.stderr.strip(): LOGGER.info('STDERR: %s',p.stderr.strip())
    LOGGER.info('EXIT CODE: %s',p.returncode)
    if check and p.returncode: raise RuntimeError(f'{cmd}: {p.stderr.strip()}')
    return p

class Console:
    def __init__(self,lang,quiet=False,no_sound=False,no_pause=False):
        self.fr=lang=='FR'
        self.tty=sys.stdout.isatty() and not quiet
        self.color=self.tty and not os.environ.get('NO_COLOR')
        self.no_sound=no_sound
        self.no_pause=no_pause
        self.started=time.monotonic()
    def tr(self,en,fr): return fr if self.fr else en
    def paint(self,text,code): return f'\033[{code}m{text}\033[0m' if self.color else text
    def say(self,text='',code='36'):
        print(self.paint(text,code),flush=True)
        LOGGER.info('SCREEN: %s',text)
    def sound(self,kind='step'):
        if self.no_sound or not self.tty: return
        try:
            if os.name=='nt':
                import winsound
                winsound.Beep(880 if kind=='done' else 560 if kind=='start' else 330,110)
            else: print('\a',end='',flush=True)
        except (OSError,RuntimeError,ImportError): LOGGER.warning('Terminal sound unavailable')
    def splash(self,root):
        self.say('═'*68,'35')
        self.say('  🦀  RUST RPG  |  THE OWNERSHIP CHRONICLES','1;33')
        self.say('  120 LEVELS  •  12 CHAPTERS  •  240 GIT BRANCHES','1;36')
        self.say('═'*68,'35')
        self.say(self.tr('What this installer will do:','Ce que cet installateur va faire :'),'1;37')
        for en,fr in [
            ('1. Check Git and Rust prerequisites.','1. Vérifier les prérequis Git et Rust.'),
            ('2. Create a new Git repository and game documentation.','2. Créer un dépôt Git et la documentation du jeu.'),
            ('3. Install validation hooks and GitHub Actions.','3. Installer les hooks de validation et GitHub Actions.'),
            ('4. Build 120 work branches and 120 solution branches.','4. Générer 120 branches de travail et 120 branches de solutions.'),
            ('5. Validate each reference solution with Cargo.','5. Valider chaque solution de référence avec Cargo.'),
            ('6. Keep solutions LOCAL unless explicitly published.','6. Garder les solutions LOCALES sauf publication explicite.')]:
            self.say('  '+self.tr(en,fr),'37')
        self.say(self.tr(f'Destination: {root}',f'Destination : {root}'),'33')
        self.say(self.tr('A detailed .log file will record all commands and results.',
                         'Un fichier .log détaillé enregistrera toutes les commandes et résultats.'),'33')
        self.sound('start')
    def menu(self):
        """Keyboard-only confirmation with a safe default; never blocks automation."""
        if not self.tty or self.no_pause:
            LOGGER.info('MENU bypassed (noninteractive or --no-pause)')
            return True
        self.say(self.tr('\n[S] Start / resume    [Q] Quit',
                         '\n[D] Démarrer / reprendre    [Q] Quitter'),'1;36')
        while True:
            try:
                choice=input(self.tr('Your choice [S]: ', 'Votre choix [D] : ')).strip().lower()
            except (EOFError,KeyboardInterrupt):
                LOGGER.info('User cancelled setup at menu')
                return False
            LOGGER.info('MENU choice=%s',choice)
            if choice in ('','s','d'):return True
            if choice in ('q','n'):return False
            self.say(self.tr('Invalid choice.','Choix invalide.'),'31')

    def phase(self,label,current,total,start):
        width=24
        ratio=current/max(1,total)
        bar='█'*round(ratio*width)+'░'*(width-round(ratio*width))
        elapsed=time.monotonic()-start
        remaining=elapsed/current*(total-current) if current else 0
        eta=f'{int(remaining//60):02d}:{int(remaining%60):02d}' if current else '--:--'
        self.say(f'  [{bar}] {current}/{total} | {label} | ETA {eta}','36')
        LOGGER.info('PHASE %s %s/%s ETA=%s',label,current,total,eta)

    def progress(self,n,branch,chapter,topic):
        width=28
        filled=round(n/120*width)
        bar='█'*filled+'░'*(width-filled)
        line=f'[{bar}] {n:3d}/120 | {branch} | {chapter}: {topic}'
        if self.tty:
            # Clear and rewrite a single progress line; preserve full events in log.
            print('\r\033[2K'+self.paint(line,'32'),end='\n',flush=True)
        else:
            print(line,flush=True)
        LOGGER.info('LEVEL %03d/120 branch=%s chapter=%s topic=%s',n,branch,chapter,topic)
    def finish(self,root,success,logfile):
        self.sound('done' if success else 'error')
        self.say('═'*68,'35')
        self.say(self.tr('SUCCESS — CAMPAIGN READY' if success else 'FAILED — SEE LOG',
                         'SUCCÈS — CAMPAGNE PRÊTE' if success else 'ÉCHEC — CONSULTER LE LOG'),
                 '1;32' if success else '1;31')
        self.say(self.tr(f'Repository: {root}',f'Dépôt : {root}'))
        self.say(self.tr(f'Log file: {logfile}',f'Journal : {logfile}'))
        self.say(self.tr(f'Elapsed: {time.monotonic()-self.started:.1f} seconds',
                         f'Durée : {time.monotonic()-self.started:.1f} secondes'))
        if success:
            self.say(self.tr('HOW TO START PLAYING', 'COMMENT COMMENCER À JOUER'),'1;33')
            steps = [
                ('1. Open a terminal in the repository:', '1. Ouvre un terminal dans le dépôt :'),
                (f'   cd "{root}"', f'   cd "{root}"'),
                ('2. Read README.md and paste MASTER_PROMPT.md into ChatGPT.', '2. Lis README.md et colle MASTER_PROMPT.md dans ChatGPT.'),
                ('3. Start the first quest:', '3. Commence la première quête :'),
                ('   git switch level-001/work', '   git switch level-001/work'),
                ('4. Read LEVEL.md, then edit src/lib.rs.', '4. Lis LEVEL.md, puis modifie src/lib.rs.'),
                ('5. Run: cargo fmt && cargo clippy --workspace --all-targets -- -D warnings && cargo test',
                 '5. Exécute : cargo fmt && cargo clippy --workspace --all-targets -- -D warnings && cargo test'),
                ('6. Commit: git add . && git commit -m "feat(level-001): complete first quest"',
                 '6. Commit : git add . && git commit -m "feat(level-001): complete first quest"'),
                ('7. Ask your Rust RPG mentor to assess your code and understanding.',
                 '7. Demande à ton professeur Rust RPG d’évaluer ton code et ta compréhension.'),
                ('8. Next: git switch level-002/work (after approval).',
                 '8. Ensuite : git switch level-002/work (après validation).'),
                ('Reference solutions remain LOCAL; do not push --all.',
                 'Les solutions restent LOCALES ; ne fais pas git push --all.')
            ]
            for en, fr in steps: self.say(self.tr(en,fr),'37')
        if self.tty and not self.no_pause:
            self.say(self.tr('Press Enter to close...', 'Appuyez sur Entrée pour fermer...'),'1;37')
            try: input()
            except (EOFError,KeyboardInterrupt): pass

def configure_logging(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.handlers.clear()
    handler=logging.FileHandler(path,mode='a',encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(message)s'))
    LOGGER.addHandler(handler)
    LOGGER.info('Rust RPG scaffolding started')

def write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8',newline='\n')

def docs(lang):
    t=FR if lang=='FR' else EN
    readme=f'''# {t['title']}

**120 levels · 12 chapters · 12 boss battles · Git-native progression**

## Quick start / Démarrage

Prerequisites: Python 3.11+, Git, Rust (`rustc`, `cargo`, `rustfmt`, `clippy`).

```bash
python scaffold.py --name rust-rpg-player
python scaffold.py FR --name rust-rpg-joueur
```

This generator is distributed separately from the generated player repository. In the generated repository:

```bash
git switch level-001/work
cargo test
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
```

## Rules / Règles

{t['rule']}

- Each level has `level-NNN/work` and `level-NNN/solutions` branches.
- Commit format: `feat(level-NNN): meaningful description` (also fix, test, refactor, docs).
- Hooks are installed using `core.hooksPath=.githooks` and check formatting, lint, tests, and commit syntax.
- GitHub Actions validates pushes and pull requests; hooks are not a security boundary.
- Solutions are generated locally, but only `main` and work branches are published by default.
- Levels are self-contained; the master prompt provides additional conceptual assessment.
- Never merge a solution branch into work to claim completion.

## Chapters

| Chapter | Levels | Focus |
|---|---|---|
'''
    for i,(name,_) in enumerate(CHAPTERS):readme+=f'| {i+1:02d} | {i*10+1:03d}–{i*10+10:03d} | {name} |\n'
    readme+='''
## Publish to GitHub

Create an empty GitHub repository first. From your generated player repository:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
python publish.py --remote origin          # only work branches
python publish.py --remote origin --solutions  # opt-in: publishes solution branches too
```

**Warning:** publishing solutions makes them visible to anyone with access to the remote repository. `git push --all` would also publish them.

## Scope and assessment

The campaign includes 120 coding checkpoints with individual APIs and acceptance assertions, 11 additional executable chapter boss modules, and a multi-crate final capstone. Many advanced chapter checkpoints remain focused *kata* exercises rather than complete production projects; Tokio, Serde, and distributed-system engineering are not yet implemented. Do not claim professional-level mastery based only on passing these tests. Do not represent the kata checks as certification of those advanced skills.

See `MASTER_PROMPT.md` for mentor instructions and `LEVEL.md` on each work branch for the level brief.
'''
    prompt=f'''# {t['title']} — MASTER PROMPT

You are a patient, rigorous Rust instructor and RPG game master. The student writes all code. Do not provide a complete solution unless the student explicitly requests it. Default language: {'French' if lang=='FR' else 'English'}. Adapt to the student's language.

## Session protocol
1. Ask for current branch, `LEVEL.md`, relevant code, and the output of `cargo test --workspace` when unavailable. Never pretend to see a repository you cannot access.
2. Explain the current level's concepts, prerequisites and acceptance criteria without solving it.
3. Offer hints in three escalating tiers: conceptual, API-oriented, then pseudocode. Give a full implementation only when requested.
4. Review correctness, ownership and borrowing, idiomatic Rust, error handling, tests and maintainability.
5. Ask at least one comprehension question. Passing automated tests alone does not prove mastery.
6. Before approving a level, request evidence of passing `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, and a correctly formatted commit.
7. Never claim to have run commands or checked GitHub without actually doing so. Allow alternative correct solutions.
8. Move to the next work branch only after approval. Never merge solution code into work.

## Git convention
`feat(level-001): implement exercise` (allowed types: feat, fix, test, refactor, docs). Use level number matching the checked-out work branch.

## Levels and learning outcomes
'''
    for i,(name,items) in enumerate(CHAPTERS):
        prompt+=f'\n### Chapter {i+1}: {name}\n'
        for j,item in enumerate(items.split('|')): prompt+=f'- {i*10+j+1:03d}: {item}\n'
    prompt+='''
## Critical pedagogical limitation

The 120 code checkpoints and executable boss labs are *practice exercises*, not complete demonstrations of all the chapter topics. For concurrency, async, FFI, macros, XML, security and other advanced topics, teach the missing concepts and assign a supplementary project before awarding chapter mastery. Never pretend the simple checkpoint alone verifies the chapter skill.

## Assessment
- Technical: passing tests, formatting, linting, and accepted commit.
- Conceptual: student can explain key tradeoffs and constraints.
- Pedagogical: no copied solution, or copied code is explicitly disclosed and discussed.
- XP is optional and never overrides failed gates.
'''
    return readme,prompt

def hook_files(root):
    pre='''#!/usr/bin/env python3
import pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parent.parent
branch=subprocess.run(['git','branch','--show-current'],cwd=root,capture_output=True,text=True).stdout.strip()
if not branch.endswith('/work'):
    sys.exit(0)
for cmd in (['cargo','fmt','--check'],['cargo','clippy','--workspace','--all-targets','--','-D','warnings'],['cargo','test','--workspace']):
    result=subprocess.run(cmd,cwd=root)
    if result.returncode: sys.exit(result.returncode)
'''
    commit='''#!/usr/bin/env python3
import pathlib,re,subprocess,sys
branch=subprocess.run(['git','branch','--show-current'],capture_output=True,text=True).stdout.strip()
if not branch.endswith('/work'):sys.exit(0)
level=branch.split('/')[0].replace('level-','')
msg=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8').splitlines()[0]
pattern=rf'(feat|fix|test|refactor|docs)\\(level-{level}\\): [a-zA-Z0-9].{{7,}}'
if not re.fullmatch(pattern,msg):
    print(f'Invalid commit. Example: feat(level-{level}): implement exercise',file=sys.stderr)
    sys.exit(1)
'''
    for name,data in [('pre-commit',pre),('commit-msg',commit)]:
        p=root/'.githooks'/name;write(p,data)
        if os.name!='nt':p.chmod(0o755)

def workflow(root):
    write(root/'.github/workflows/validate.yml','''name: Rust RPG validation
on: [push, pull_request]
jobs:
  rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - run: cargo fmt --check
        if: hashFiles('Cargo.toml') != ''
      - run: cargo clippy --workspace --all-targets -- -D warnings
        if: hashFiles('Cargo.toml') != ''
      - run: cargo test
        if: hashFiles('Cargo.toml') != ''
''')
    write(root/'.github/workflows/audit-solutions.yml', '''name: Audit all Rust RPG solutions
# Explicit opt-in: solutions are private by default. First publish them using
# python publish.py --remote origin --solutions, then trigger this workflow.
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Fetch published level branches
        run: |
          git fetch origin '+refs/heads/level-*:refs/remotes/origin/level-*'
          for branch in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/level-); do
            git branch "${branch#origin/}" "$branch"
          done
      - name: Verify all 120 reference solutions
        run: python audit.py . --cargo --report rust-rpg-cargo-audit.json
      - name: Upload audit evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: rust-rpg-cargo-audit
          path: rust-rpg-cargo-audit.json
          if-no-files-found: warn
''')

def publish_script():
    return '''#!/usr/bin/env python3
import argparse, subprocess
p=argparse.ArgumentParser(description='Publish Rust RPG branches')
p.add_argument('--remote',default='origin');p.add_argument('--solutions',action='store_true')
a=p.parse_args()
branches=subprocess.check_output(['git','branch','--format=%(refname:short)'],text=True).splitlines()
selected=['main']+[b for b in branches if b.endswith('/work') or (a.solutions and b.endswith('/solutions'))]
for branch in selected:
    subprocess.run(['git','push',a.remote,f'{branch}:{branch}'],check=True)
print(f'Published {len(selected)} branches')
'''

def level_files(root,n,lang,solution):
    if n == 120:
        create_capstone(root, lang, solution)
        level_doc = root/'LEVEL.md'
        level_doc.write_text(level_doc.read_text(encoding='utf-8') + boss_guide(n, lang), encoding='utf-8')
        return
    t=FR if lang=='FR' else EN
    chapter=(n-1)//10; index=(n-1)%10
    name=CHAPTERS[chapter][1].split('|')[index]
    quest=CORE_QUESTS.get(n, PROJECT_QUESTS.get(n, INTEGRATION_QUESTS.get(n, QUESTS[n-1])))
    fn,args,ret,impl=quest.name,quest.args,quest.returns,quest.solution
    generics = GENERIC_SIGNATURES.get(n, ("", ""))[0]
    body=impl if solution else 'todo!("Complete this level")'
    pedagogical_lints = {20: 'clippy::ptr_arg', 26: 'clippy::manual_unwrap_or, clippy::manual_unwrap_or_default', 48: 'clippy::needless_lifetimes', 101: 'clippy::unnecessary_fold'}
    lint_attr = f'#[allow({pedagogical_lints[n]})]\n' if n in pedagogical_lints else ''
    lib=f'/// Level {n:03d}: {name}.\n{lint_attr}pub fn {fn}{generics}({args}) -> {ret} {{\n    {body}\n}}\n\n#[cfg(test)]\nmod tests {{\n    use super::*;\n    #[test]\n    fn acceptance() {{\n        {quest.assertions}\n    }}\n}}\n'
    boss = index == 9
    if boss:
        lib += '\npub mod boss;\n'
        write(root/'src/boss.rs', render_boss(n, solution))
    write(root/'src/lib.rs',lib)
    write(root/'Cargo.toml',f'[package]\nname = "rust_rpg_level_{n:03d}"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n')
    objective = quest.description if lang=='EN' else f'Exercice : {name}. {quest.description}'
    boss = index == 9
    mission = ('Boss battle: integrate the chapter concepts.' if lang=='EN' else 'Combat de boss : intégrer les concepts du chapitre.') if boss else ('Implement and explain your design decisions.' if lang=='EN' else 'Implémente et explique tes choix de conception.')
    write(root/'LEVEL.md',f'# Level {n:03d} — {name}\n\n**Chapter:** {CHAPTERS[chapter][0]}\n\n**{t["objective"]}:** {objective}\n\n{t["task"]}\n\n**API:** `pub fn {fn}{generics}({args}) -> {ret}`\n\n**{t["mission"]}:** {mission}\n\n**Validation:** `cargo fmt --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`.\n\n**Important:** Some advanced labs require local loopback networking or a platform C runtime. Dependency-free async exercises demonstrate futures and polling, not Tokio itself. Full integration capstones are still in development.\n' + (boss_guide(n, lang) + ('\n**Executable boss API:** `src/boss.rs` (run `cargo test --workspace`).\n' if lang=='EN' else '\n**API du boss testée :** `src/boss.rs` (lancer `cargo test --workspace`).\n') if boss else ''))

def main():
    p=argparse.ArgumentParser(description='Generate a bilingual 120-level Rust RPG Git repository')
    p.add_argument('language',nargs='?',default='EN',type=str.upper,choices=['EN','FR'])
    p.add_argument('--name',default='rust-rpg-player')
    p.add_argument('--output',type=Path,default=Path.cwd())
    p.add_argument('--skip-cargo-validation',action='store_true',help='Only for testing generator on machines without Rust; not recommended')
    p.add_argument('--no-sound',action='store_true',help='Disable terminal sounds')
    p.add_argument('--no-pause',action='store_true',help='Do not wait for Enter at the end')
    p.add_argument('--quiet',action='store_true',help='Disable colors and sounds (CI mode)')
    p.add_argument('--resume',action='store_true',help='Resume an interrupted generation; preserve completed branches')
    a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',a.name):p.error('Invalid repository name')
    root=a.output.resolve()/a.name
    logpath=a.output.resolve()/(a.name+'-scaffold.log')
    configure_logging(logpath)
    ui=Console(a.language,a.quiet,a.no_sound,a.no_pause)
    ui.splash(root)
    success=False
    cancelled=False
    try:
        if not shutil.which('git'):raise RuntimeError('Git is required')
        if not a.skip_cargo_validation and not shutil.which('cargo'):raise RuntimeError('Cargo/Rust is required')
        if not ui.menu():
            cancelled=True
            LOGGER.info('Generation cancelled before filesystem changes')
            return
        if root.exists() and not a.resume:raise RuntimeError(f'Destination exists: {root}; use --resume to continue')
        if a.resume and (not root.is_dir() or not (root/'.git').exists()):
            raise RuntimeError('--resume requires an existing generated Git repository')
        ui.say(ui.tr('Prerequisites OK. Creating repository...', 'Prérequis validés. Création du dépôt...'),'32')
        if not a.resume:
            root.mkdir(parents=True)
            run(['git','init','-b','main'],root)
            run(['git','config','user.name','Rust RPG Generator'],root)
            run(['git','config','user.email','generator@rust-rpg.invalid'],root)
            readme,prompt=docs(a.language)
            write(root/'README.md',readme);write(root/'MASTER_PROMPT.md',prompt)
            write(root/'publish.py',publish_script())
            write(root/'.gitignore','/target/\n*.log\n')
            hook_files(root);workflow(root)
            # Ship the independent verifier with the player repository so GitHub
            # Actions can audit every published solution without the generator kit.
            write(root/'audit.py', Path(__file__).with_name('audit.py').read_text(encoding='utf-8'))
            run(['git','add','.'],root)
            run(['git','commit','-m','docs: initialize Rust RPG campaign'],root)
            run(['git','config','core.hooksPath','.githooks'],root)
        else:
            LOGGER.info('RESUME mode: existing repository=%s',root)
            current=run(['git','branch','--show-current'],root).stdout.strip()
            if current != 'main':
                # An interrupted generation may leave an uncommitted level checkout.
                # Refuse to discard unrelated user changes without explicit confirmation.
                dirty=run(['git','status','--porcelain'],root).stdout.strip()
                if dirty:
                    if not re.fullmatch(r'level-\d{3}/(?:work|solutions)',current):
                        raise RuntimeError('Refusing to discard changes outside a generated level branch')
                    LOGGER.warning('Discarding interrupted scaffold changes on %s',current)
                    run(['git','reset','--hard','HEAD'],root)
                    run(['git','clean','-fd'],root)
                run(['git','switch','--quiet','main'],root)
                # A branch without a level commit was interrupted and must be rebuilt.
                head=run(['git','rev-parse','main'],root).stdout.strip()
                branch_head=run(['git','rev-parse',current],root).stdout.strip()
                if current.startswith('level-') and head==branch_head:
                    run(['git','branch','-D',current],root)
            if run(['git','status','--porcelain'],root).stdout.strip():
                raise RuntimeError('Cannot resume with uncommitted changes on main')
        existing=set(run(['git','branch','--format=%(refname:short)'],root).stdout.splitlines())
        phase_start=time.monotonic()
        validation_start=time.monotonic()
        validated=0
        for n in range(1,121):
            base=f'level-{n:03d}'
            chapter,items=CHAPTERS[(n-1)//10]
            topic=items.split('|')[(n-1)%10]
            for suffix,solution in [('work',False),('solutions',True)]:
                branch=f'{base}/{suffix}'
                if branch in existing:
                    LOGGER.info('RESUME SKIP existing completed branch %s',branch)
                    continue
                run(['git','switch','--quiet','main'],root)
                run(['git','switch','--quiet','-c',branch,'main'],root)
                level_files(root,n,a.language,solution)
                # Format before committing: reference solutions must be reproducible.
                # Format work branches as well, so starter tests satisfy rustfmt.
                if shutil.which('cargo'):
                    run(['cargo','fmt','--all'],root)
                elif solution:
                    LOGGER.warning('Cargo missing: solution %s cannot be formatted locally',branch)
                if solution and not a.skip_cargo_validation:
                    for cmd,label in [(['cargo','fmt','--check'],'format'),(['cargo','clippy','--workspace','--all-targets','--','-D','warnings'],'clippy'),(['cargo','test','--workspace'],'tests')]:
                        ui.phase(f'Cargo {label} · level {n:03d}',validated,360,validation_start)
                        run(cmd,root)
                        validated+=1
                run(['git','add','.'],root)
                run(['git','-c','core.hooksPath=/dev/null','commit','--quiet','-m',f'docs: scaffold {branch}'],root)
                existing.add(branch)
            ui.phase(f'Git · {chapter} / {topic}',n,120,phase_start)
            ui.progress(n,base,chapter,topic)
            if n%10==0:ui.sound('step')
        run(['git','switch','--quiet','main'],root)
        success=True
        LOGGER.info('Generation complete: 241 branches, language=%s',a.language)
    except Exception:
        LOGGER.exception('Generation failed')
        ui.say(ui.tr('An error occurred. See the detailed log.',
                     'Une erreur est survenue. Consultez le journal détaillé.'),'1;31')
        raise
    finally:
        if cancelled:
            ui.say(ui.tr("Setup cancelled; no files created.","Installation annulée; aucun fichier créé."),"33")
        else:
            ui.finish(root,success,logpath)

if __name__=='__main__':main()
