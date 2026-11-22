import tempfile
import unittest
from pathlib import Path
from scaffold import CHAPTERS, docs, level_files, Console
from quest_catalog import QUESTS

class GeneratorTests(unittest.TestCase):
    def test_120_unique_levels(self):
        self.assertEqual(len(QUESTS), 120)
        self.assertEqual(len({q.name for q in QUESTS}),120)
        self.assertEqual(sum(len(x.split('|')) for _,x in CHAPTERS),120)
    def test_bilingual(self):
        self.assertIn('Les Chroniques',docs('FR')[0])
        self.assertIn('Ownership Chronicles',docs('EN')[0])
    def test_every_level_has_assertions(self):
        for q in QUESTS:
            self.assertIn('assert',q.assertions)
            self.assertTrue(q.solution)
    def test_generated_files_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            level_files(root,120,'FR',True)
            self.assertIn('pub fn parse', (root/'crates/rpg-core/src/lib.rs').read_text())
            self.assertIn('Objectif',(root/'LEVEL.md').read_text())
            level_files(root,1,'EN',False)
            self.assertIn('binding',(root/'src/lib.rs').read_text())
            self.assertIn('todo!',(root/'src/lib.rs').read_text())
    def test_advanced_labs_use_real_rust_mechanisms(self):
        from integration_labs import INTEGRATION_QUESTS
        self.assertEqual(len(INTEGRATION_QUESTS), 30)
        for level in range(81, 111):
            self.assertIn(level, INTEGRATION_QUESTS)
            self.assertIn('assert', INTEGRATION_QUESTS[level].assertions)
        self.assertIn('std::thread::spawn', INTEGRATION_QUESTS[81].solution)
        self.assertIn('TcpListener::bind', INTEGRATION_QUESTS[96].solution)
        self.assertIn('macro_rules!', INTEGRATION_QUESTS[101].solution)
        self.assertIn('unsafe', INTEGRATION_QUESTS[103].solution)

    def test_advanced_branch_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            level_files(root, 96, 'EN', True)
            self.assertIn('TcpListener::bind', (root/'src/lib.rs').read_text())
            level_files(root, 96, 'FR', False)
            self.assertIn('todo!', (root/'src/lib.rs').read_text())
            self.assertNotIn('TcpListener::bind', (root/'src/lib.rs').read_text())

    def test_finish_shows_play_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            from unittest.mock import patch
            from io import StringIO
            output=StringIO()
            with patch('sys.stdout',output):
                Console('FR',quiet=True,no_pause=True).finish(Path(tmp),True,Path(tmp)/'game.log')
            self.assertIn('COMMENT COMMENCER',output.getvalue())
            self.assertIn('git switch level-001/work',output.getvalue())
if __name__=='__main__':unittest.main()

class ProjectLabTests(unittest.TestCase):
    def test_project_labs_are_complete(self):
        from project_labs import PROJECT_QUESTS
        self.assertEqual(set(PROJECT_QUESTS),set(range(71,81))|set(range(111,121)))
        for quest in PROJECT_QUESTS.values():
            self.assertTrue(quest.solution)
            self.assertIn('assert',quest.assertions)
    def test_generated_project_branch_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            from scaffold import level_files
            root=Path(tmp)
            level_files(root,72,'EN',True)
            self.assertIn('read_to_string',(root/'src/lib.rs').read_text())
            level_files(root,72,'FR',False)
            self.assertNotIn('read_to_string',(root/'src/lib.rs').read_text())
            self.assertIn('todo!',(root/'src/lib.rs').read_text())

class CoreLabTests(unittest.TestCase):
    def test_forty_core_levels_are_unique_and_covered(self):
        from core_labs import CORE_QUESTS
        self.assertEqual(set(CORE_QUESTS),set(range(31,51)) | set(range(61,71)))
        for quest in CORE_QUESTS.values():
            self.assertTrue(quest.solution)
            self.assertIn('assert',quest.assertions)
    def test_generic_signatures_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            level_files(root,48,'EN',True)
            self.assertIn("pub fn first_view<'a, T>",(root/'src/lib.rs').read_text())
            level_files(root,48,'FR',False)
            self.assertIn('todo!',(root/'src/lib.rs').read_text())
            self.assertNotIn('values.first()', (root/'src/lib.rs').read_text())

class CapstoneTests(unittest.TestCase):
    def test_multicrate_work_and_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            level_files(root,120,'EN',True)
            self.assertIn('members =', (root/'Cargo.toml').read_text())
            self.assertIn('checked_add', (root/'crates/rpg-core/src/lib.rs').read_text())
            self.assertIn('end_to_end_file', (root/'crates/rpg-cli/tests/pipeline.rs').read_text())
            level_files(root,120,'FR',False)
            self.assertIn('todo!', (root/'crates/rpg-core/src/lib.rs').read_text())
            self.assertNotIn('checked_add', (root/'crates/rpg-core/src/lib.rs').read_text())
            self.assertIn('Projet final', (root/'LEVEL.md').read_text())

class BossGuideTests(unittest.TestCase):
    def test_all_boss_guides(self):
        from boss_guides import BOSSES, guide
        self.assertEqual(set(BOSSES), set(range(10,121,10)))
        self.assertIn('Integration challenge', guide(90,'EN'))
        self.assertIn('Défi intégrateur', guide(90,'FR'))
    def test_generated_boss_guides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            level_files(root,90,'FR',False)
            self.assertIn('Défi intégrateur', (root/'LEVEL.md').read_text())
            level_files(root,120,'EN',True)
            self.assertIn('Integration challenge', (root/'LEVEL.md').read_text())

class AuditTests(unittest.TestCase):
    def test_missing_repository_is_rejected(self):
        from audit import audit
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                audit(Path(tmp))

    def test_missing_cargo_fails_explicitly(self):
        from audit import audit
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'.git').mkdir()
            with patch('audit.shutil.which', return_value=None):
                with self.assertRaisesRegex(RuntimeError, 'Cargo not installed'):
                    audit(Path(tmp), cargo=True)

    def test_read_only_audit_does_not_switch_branches(self):
        import subprocess
        from audit import audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git','init','-q','-b','main'],cwd=root,check=True)
            (root/'uncommitted.txt').write_text('keep this')
            result = audit(root)
            self.assertEqual(len(result['missing_branches']),240)
            self.assertFalse(result['ok'])
            self.assertEqual(result['status'],'failed')
            self.assertEqual((root/'uncommitted.txt').read_text(),'keep this')

class RemoteAuditWorkflowTests(unittest.TestCase):
    def test_generated_remote_audit_is_explicit_and_reproducible(self):
        from scaffold import workflow
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow(root)
            content = (root/'.github/workflows/audit-solutions.yml').read_text()
            self.assertIn('workflow_dispatch:', content)
            self.assertIn('fetch-depth: 0', content)
            self.assertIn('python audit.py . --cargo', content)
            self.assertIn('upload-artifact', content)
    def test_audit_module_is_valid_python(self):
        import ast
        ast.parse(Path(__file__).with_name('audit.py').read_text())

class ExecutableBossTests(unittest.TestCase):
    def test_eleven_executable_boss_modules(self):
        from boss_labs import BOSS_LABS
        self.assertEqual(set(BOSS_LABS), set(range(10, 120, 10)))
        for level in BOSS_LABS:
            with self.subTest(level=level), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                level_files(root, level, 'EN', True)
                self.assertIn('pub mod boss;', (root/'src/lib.rs').read_text())
                boss = (root/'src/boss.rs').read_text()
                self.assertIn('boss_acceptance', boss)
                self.assertNotIn('todo!', boss)
                level_files(root, level, 'FR', False)
                self.assertIn('todo!', (root/'src/boss.rs').read_text())
                self.assertIn('API du boss', (root/'LEVEL.md').read_text())

class ReleaseRegressionTests(unittest.TestCase):
    def test_known_clippy_regressions(self):
        from scaffold import level_files
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for level, expected in [(1, 'value * 2'), (53, 'values.len()')]:
                level_files(root, level, 'EN', True)
                self.assertIn(expected, (root/'src/lib.rs').read_text(encoding='utf-8'))
            for level, lint in [(20, 'ptr_arg'), 
                                (48, 'needless_lifetimes'), (101, 'unnecessary_fold')]:
                level_files(root, level, 'EN', True)
                self.assertIn(f'#[allow(clippy::{lint})]', (root/'src/lib.rs').read_text(encoding='utf-8'))

    def test_formatter_runs_before_commit(self):
        from pathlib import Path
        code = (Path(__file__).parent/'scaffold.py').read_text(encoding='utf-8')
        self.assertLess(code.index("run(['cargo','fmt','--all'],root)"),
                        code.index("run(['git','add','.'],root)", code.index("run(['cargo','fmt','--all'],root)")))


class WindowsCargoRetryRegressionTests(unittest.TestCase):
    def test_audit_retries_only_transient_access_denied(self):
        from pathlib import Path
        source = (Path(__file__).parent / 'audit.py').read_text(encoding='utf-8')
        self.assertIn("'os error 5' in stderr.lower()", source)
        self.assertIn('attempts >= 3', source)
        self.assertIn("emit('cargo_retry'", source)

    def test_release_check_reports_retry(self):
        from pathlib import Path
        source = (Path(__file__).parent / 'release_check.py').read_text(encoding='utf-8')
        self.assertIn("event == 'cargo_retry'", source)
