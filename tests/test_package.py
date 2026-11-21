import contextlib
import importlib.util
import io
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("package", SOURCE / "scripts/package.py")
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        for name in package.SHARED_FILES:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, dest)
        for name in package.RESOURCE_DIRS:
            shutil.copytree(SOURCE / name, self.root / name)
        self.patch = patch.object(package, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_build_uses_allowlist_without_traversing_customer_data(self):
        customer = self.root / "accounts"
        customer.mkdir()
        (customer / "private.txt").write_text("synthetic private data")
        for name in (".copilot/lock", "unrelated.txt", "docs/unrelated.md",
                     ".github/skills/evaluate/token.json",
                     ".github/hooks/account-guard.json", "scripts/account_guard.py",
                     "scripts/questions.py"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not a package input")
        iterdir = Path.iterdir

        def guarded_iterdir(path):
            if path == customer:
                self.fail("packaging traversed the customer directory")
            return iterdir(path)

        output = Path(self.temp.name) / "output"
        with patch.object(Path, "iterdir", guarded_iterdir), \
                patch("sys.argv", ["package.py", "--output-dir", str(output)]), \
                contextlib.redirect_stdout(io.StringIO()):
            package.main()
        archive, = output.glob("*.zip")
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            self.assertIn("leadership-team/.github/skills/evaluate/SKILL.md", names)
            self.assertFalse(any("/skills/convene/" in name for name in names))
            self.assertIn("leadership-team/.github/skills/brainstorm/SKILL.md", names)
            self.assertIn("leadership-team/.github/skills/scope/SKILL.md", names)
            self.assertIn("leadership-team/.github/skills/define-team/SKILL.md", names)
            self.assertIn("leadership-team/scripts/teams.py", names)
            self.assertIn("leadership-team/scripts/profiles.py", names)
            self.assertIn("leadership-team/.github/skills/person-profile/SKILL.md", names)
            self.assertIn("leadership-team/tests/test_profiles.py", names)
            self.assertIn("leadership-team/docs/TEAMS-USER-GUIDE.md", names)
            self.assertIn("leadership-team/tests/test_teams.py", names)
            self.assertFalse(any("/.github/hooks/" in n or n.endswith("/account_guard.py")
                                 or n.endswith("/questions.py") for n in names))
            self.assertFalse(any("private.txt" in n or "unrelated" in n or
                                 "token.json" in n or "/.copilot/" in n for n in names))
            extracted = Path(self.temp.name) / "extracted"
            z.extractall(extracted)
        project = extracted / "leadership-team"
        result = subprocess.run(["python3", "scripts/accounts.py", "new", "synthetic"],
                                cwd=project, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / "accounts/synthetic/company/index.md").is_file())
        result = subprocess.run(
            ["python3", "scripts/teams.py", "new", "synthetic", "core", "--leader", "leader",
             "--participant", "cfo", "--purpose", "Synthetic strategic decisions"],
            cwd=project, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(["python3", "scripts/teams.py", "resolve", "synthetic", "core"],
                                cwd=project, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"team": "core"', result.stdout)
        for args in (
            ["new", "synthetic", "alex", "--person", "Alex Example",
             "--title", "Database Lead", "--area", "technical"],
            ["check", "synthetic", "alex"],
        ):
            result = subprocess.run(["python3", "scripts/profiles.py", *args],
                                    cwd=project, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_symlink_resource_is_rejected_without_following_it(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        (self.root / ".github/skills/external").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            list(package.files())

    def test_symlink_parent_is_rejected(self):
        original = self.root / "company-template"
        target = self.root / "template-original"
        original.rename(target)
        original.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            list(package.files())

    def test_missing_required_input_is_reported(self):
        (self.root / "scripts/accounts.py").unlink()
        with self.assertRaisesRegex(ValueError, "Required package input is missing"):
            list(package.files())

    def test_customer_output_directory_is_rejected(self):
        output = self.root / "accounts/synthetic"
        with patch("sys.argv", ["package.py", "--output-dir", str(output)]), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                package.main()
        self.assertEqual(exc.exception.code, 2)
        self.assertFalse(output.exists())

    def test_desktop_packaging_flag_is_not_silently_accepted(self):
        with patch("sys.argv", ["package.py", "--code"]), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                package.main()
        self.assertEqual(exc.exception.code, 2)
