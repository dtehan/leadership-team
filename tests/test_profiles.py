import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(SOURCE / "company-template", self.root / "company-template")
        self.run_script("accounts", "new", "synthetic")
        self.account = self.root / "accounts/synthetic"
        self.profiles = self.account / "company/profiles"

    def run_script(self, name, *args, success=True):
        result = subprocess.run(["python3", f"scripts/{name}.py", *args],
                                cwd=self.root, text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ERROR:", result.stderr)
        return result.stdout if success else result.stderr

    def new(self, identifier="alex", *args, success=True):
        return self.run_script("profiles", "new", "synthetic", identifier,
                               "--title", "Database Lead", "--area", "technical",
                               *args, success=success)

    def snapshot(self):
        return {p.relative_to(self.account): p.read_bytes()
                for p in self.account.rglob("*") if p.is_file()}

    def test_scaffold_is_indexable_but_stays_thin_until_evidence_review(self):
        self.new("alex", "--person", "Alex O'Example", "--area", "strategy")
        profile = self.profiles / "alex"
        self.assertTrue((profile / "sources").is_dir())
        self.assertIn("areas: [technical, strategy]", (profile / "index.md").read_text())
        self.assertIn("Unknown; no person-specific evidence", (profile / "persona.md").read_text())
        self.assertIn("evidence_status: pending",
                      self.run_script("profiles", "check", "synthetic", "alex"))
        self.run_script("build_index", "synthetic")
        self.run_script("build_index", "synthetic", "--check")
        self.assertIn("Alex O'Example", (self.profiles / "index.md").read_text())
        self.run_script("teams", "new", "synthetic", "database", "--leader", "alex",
                        "--participant", "cto", "--purpose", "Synthetic database decisions")
        room = json.loads(self.run_script("teams", "resolve", "synthetic", "database"))
        self.assertTrue(room["leader"]["thin"])
        self.assertTrue(any("alex: thin" in w for w in room["warnings"]))
        index = profile / "index.md"
        before = index.read_text()
        for status, thin in (("thin", True), ("grounded", False), ("unsupported", None)):
            with self.subTest(status=status):
                index.write_text(before.replace("evidence_status: pending", f"evidence_status: {status}"))
                if thin is None:
                    self.assertIn("invalid evidence_status", self.run_script(
                        "profiles", "check", "synthetic", "alex", success=False))
                else:
                    room = json.loads(self.run_script("teams", "resolve", "synthetic", "database"))
                    self.assertEqual(room["leader"]["thin"], thin)

    def test_explicit_generic_role_remains_thin(self):
        self.new("database-lead", "--generic")
        index = (self.profiles / "database-lead/index.md").read_text()
        self.assertIn('person: "TBD"', index)
        self.assertIn("evidence_status: generic", index)
        self.assertIn("Explicit generic", (self.profiles / "database-lead/persona.md").read_text())
        self.run_script("profiles", "check", "synthetic", "database-lead")
        self.assertIn("Generic Database Lead\tDatabase Lead\tTHIN",
                      self.run_script("teams", "profiles", "synthetic"))

    def test_existing_profile_is_not_overwritten(self):
        self.new("alex", "--person", "Alex Example")
        before = self.snapshot()
        for identifier in ("alex", "leader"):
            with self.subTest(identifier=identifier):
                self.assertIn("already exists",
                              self.new(identifier, "--person", "Someone Else", success=False))
                self.assertEqual(before, self.snapshot())

    def test_invalid_inputs_fail_before_writing(self):
        before = self.snapshot()
        for identifier, args in (
                ("../escape", ("--person", "Alex")),
                ("moonshot", ("--person", "Alex")),
                ("bad-name", ("--person", "Alex\nperson: Someone Else")),
                ("bad-title", ("--person", "Alex", "--title", 'Lead "Example"')),
                ("bad-area", ("--person", "Alex", "--area", "../other")),
                ("unknown-person", ("--person", "TBD"))):
            with self.subTest(identifier=identifier):
                self.new(identifier, *args, success=False)
                self.assertEqual(before, self.snapshot())
        self.assertIn("Invalid slug", self.run_script(
            "profiles", "new", "../outside", "alex", "--person", "Alex",
            "--title", "Lead", "--area", "technical", success=False))

    def test_missing_template_fails_before_creating_profile(self):
        (self.account / "company/_templates/persona.md").unlink()
        self.new("alex", "--person", "Alex", success=False)
        self.assertFalse((self.profiles / "alex").exists())

    def test_symlink_paths_cannot_escape_or_alias_profiles(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.profiles / "escape").symlink_to(outside, target_is_directory=True)
        self.assertIn("symlinks", self.new("escape", "--person", "Alex", success=False))
        self.assertEqual(list(outside.iterdir()), [])
        self.new("alex", "--person", "Alex")
        persona = self.profiles / "alex/persona.md"
        persona.unlink()
        external = outside / "persona.md"
        external.write_text("External source must not be read.")
        persona.symlink_to(external)
        self.assertIn("escapes", self.run_script(
            "profiles", "check", "synthetic", "alex", success=False))
        self.assertEqual(external.read_text(), "External source must not be read.")

    def test_structural_check_rejects_missing_document_metadata(self):
        self.new("alex", "--person", "Alex")
        doc = self.profiles / "alex/bio.md"
        doc.write_text("---\nsummary: Source without attribution\n---\n")
        self.assertIn("missing scalar as_of", self.run_script(
            "profiles", "check", "synthetic", "alex", success=False))

    def test_structural_check_enforces_document_date_and_attribution_shape(self):
        self.new("alex", "--person", "Alex")
        persona = self.profiles / "alex/persona.md"
        original = persona.read_text()
        date_line = next(line for line in original.splitlines() if line.startswith("as_of:"))
        for replacement, expected in (
                ("as_of: 20261117", "as_of must be YYYY-MM-DD"),
                ("as_of: 2026-02-31", "as_of must be YYYY-MM-DD"),
                ("as_of: [2026-11-17]", "missing scalar as_of")):
            with self.subTest(replacement=replacement):
                persona.write_text(original.replace(date_line, replacement))
                self.assertIn(expected, self.run_script(
                    "profiles", "check", "synthetic", "alex", success=False))
        persona.write_text(original.replace("roles: [alex]", "roles: [cto]"))
        self.assertIn("roles must include alex", self.run_script(
            "profiles", "check", "synthetic", "alex", success=False))

    def test_existing_profiles_do_not_require_new_evidence_metadata(self):
        persona = self.profiles / "cto/persona.md"
        persona.write_text("Existing authored dossier.\n")
        index = self.profiles / "cto/index.md"
        index.write_text(index.read_text().replace("person: TBD", "person: Existing Example"))
        self.run_script("teams", "new", "synthetic", "platform", "--leader", "cto",
                        "--participant", "coo", "--purpose", "Synthetic platform decisions")
        room = json.loads(self.run_script("teams", "resolve", "synthetic", "platform"))
        self.assertFalse(room["leader"]["thin"])

    def test_profile_memory_is_not_indexed_or_checked_as_researched_evidence(self):
        self.new("alex", "--person", "Alex Example")
        memory = self.profiles / "alex/memory.md"
        memory.write_text("# Simulation memory\n\nNot public professional evidence.\n")
        self.run_script("profiles", "check", "synthetic", "alex")
        self.run_script("build_index", "synthetic")
        self.run_script("build_index", "synthetic", "--check")
        self.assertNotIn("memory.md", (self.profiles / "alex/index.md").read_text())

    def test_team_memory_import_preserves_history_and_is_repeatable(self):
        self.new("alex", "--person", "Alex Example")
        target = self.profiles / "alex/memory.md"
        original = b"# Simulation memory\n\n## Past Decisions\n\nExisting profile history.\n"
        target.write_bytes(original)
        for team in ("dba", "platform"):
            directory = self.account / "teams" / team / "memories"
            directory.mkdir(parents=True)
            source = directory / "alex.md"
            content = f"### Old {team} decision\nOriginal insight.\n".encode()
            source.write_bytes(content)
            args = ("migrate-memory", "synthetic", "alex", "--team", team)
            self.assertIn("Imported", self.run_script("profiles", *args))
            imported = target.read_bytes()
            self.assertTrue(imported.startswith(original))
            self.assertIn(content, imported)
            self.assertIn(f"Imported history - team {team}".encode(), imported)
            self.assertEqual(source.read_bytes(), content)
            self.assertIn("Already imported", self.run_script("profiles", *args))
            self.assertEqual(target.read_bytes(), imported)
            original = imported
        source.write_bytes(content + b"New legacy entry.\n")
        self.assertIn("reconcile it manually", self.run_script("profiles", *args, success=False))
        self.assertEqual(target.read_bytes(), imported)

    def test_memory_import_creates_profile_memory_and_rejects_invalid_paths(self):
        directory = self.account / "teams/dba/memories"
        directory.mkdir(parents=True)
        source = directory / "cto.md"
        source.write_text("Original CTO memory.\n")
        args = ("migrate-memory", "synthetic", "cto", "--team", "dba")
        self.run_script("profiles", *args)
        target = self.profiles / "cto/memory.md"
        self.assertIn("## Past Decisions", target.read_text())
        before = self.snapshot()
        for identifier, team in (("absent", "dba"), ("moonshot", "dba"),
                                 ("../cto", "dba"), ("cto", "../outside"),
                                 ("cto", "missing")):
            with self.subTest(identifier=identifier, team=team):
                self.run_script("profiles", "migrate-memory", "synthetic", identifier,
                                "--team", team, success=False)
                self.assertEqual(before, self.snapshot())
        source.unlink()
        source.symlink_to(target)
        self.assertIn("symlink", self.run_script("profiles", *args, success=False))
        source.unlink()
        source.write_text("Legacy.\n")
        target.unlink()
        target.symlink_to(self.profiles / "cfo/index.md")
        self.assertIn("symlink", self.run_script("profiles", *args, success=False))


if __name__ == "__main__":
    unittest.main()
