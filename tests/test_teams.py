import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


class TeamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(SOURCE / "company-template", self.root / "company-template")
        self.run_script("accounts", "new", "synthetic")
        self.account = self.root / "accounts/synthetic"
        for identifier, title in (("alex", "DBA Lead"), ("sam", "Database Engineer"),
                                  ("ciso", "Security Advisor")):
            directory = self.account / "company/profiles" / identifier
            directory.mkdir()
            (directory / "index.md").write_text(
                f"---\nperson: {identifier.title()} Example\ntitle: {title}\n"
                "areas: [technical, strategy]\n---\n")
            (directory / "persona.md").write_text("Generic synthetic test profile.\n")

    def run_script(self, name, *args, success=True):
        result = subprocess.run(["python3", f"scripts/{name}.py", *args],
                                cwd=self.root, text=True, capture_output=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ERROR:", result.stderr)
        return result.stdout if success else result.stderr

    def teams(self, *args, success=True):
        return self.run_script("teams", *args, success=success)

    def new(self, team="dba", leader="alex", participants=("sam",), *extra):
        args = ["new", "synthetic", team, "--leader", leader, "--purpose", "Synthetic decisions"]
        for person in participants:
            args.extend(("--participant", person))
        return self.teams(*args, *extra)

    def definition(self, team="dba"):
        return self.account / "teams" / team / "team.json"

    def rewrite(self, definition):
        self.definition().write_text(json.dumps(definition))

    def test_overlapping_teams_resolve_independently_without_changing_profiles(self):
        before = {p: p.read_bytes() for p in (self.account / "company/profiles").rglob("*.md")}
        self.new("core", "leader", ("cfo", "cto", "coo"))
        self.new("extended", "leader", ("cfo", "cto", "coo", "alex", "ciso"))
        self.new()
        for team, leader, participants in (
                ("core", "leader", ["cfo", "cto", "coo"]),
                ("extended", "leader", ["cfo", "cto", "coo", "alex", "ciso"]),
                ("dba", "alex", ["sam"])):
            with self.subTest(team=team):
                room = json.loads(self.teams("resolve", "synthetic", team, "--input-team", team))
                self.assertEqual(room["team"], team)
                self.assertEqual(room["leader"]["profile"], leader)
                self.assertEqual([p["profile"] for p in room["participants"]], participants)
                self.assertEqual(room["workspace"], f"teams/{team}")
                self.assertTrue(all(p["vote"] for p in room["participants"]))
                self.assertEqual(room["team_snapshot"], json.loads(self.definition(team).read_text()))
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertIn("alex", self.teams("profiles", "synthetic"))
        self.assertNotIn("moonshot\t", self.teams("profiles", "synthetic"))
        self.assertIn("extended", self.teams("list", "synthetic"))

    def test_missing_and_conflicting_selection_never_falls_back_to_core(self):
        self.new()
        self.assertIn("No team", self.teams("resolve", "synthetic", "missing", success=False))
        self.assertIn("Team conflict", self.teams(
            "resolve", "synthetic", "dba", "--input-team", "core", success=False))
        result = subprocess.run(["python3", "scripts/teams.py", "resolve", "synthetic"],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("team", result.stderr)

    def test_profile_memory_follows_a_person_between_team_assignments(self):
        self.new("dba", "alex", ("sam",), "--advisor", "ciso")
        self.new("security", "ciso", ("alex",), "--facilitation", "contrarian")
        memory = self.account / "company/profiles/alex/memory.md"
        memory.write_text("### Prior simulation\n**Team**: dba\nKeep the capacity safeguard.\n")
        before = memory.read_bytes()
        dba = json.loads(self.teams("resolve", "synthetic", "dba"))
        security = json.loads(self.teams("resolve", "synthetic", "security"))
        self.assertEqual(dba["leader"]["memory"], security["participants"][0]["memory"])
        self.assertEqual(dba["leader"]["memory"], "company/profiles/alex/memory.md")
        self.assertEqual(dba["participants"][-1]["memory"], security["leader"]["memory"])
        self.assertEqual(memory.read_bytes(), before)
        self.assertFalse((self.account / "teams/dba/memories").exists())
        self.assertTrue((self.account / "teams/security/memories").is_dir())

    def test_profile_memory_cannot_resolve_outside_the_account(self):
        self.new()
        outside = self.root / "external-memory.md"
        outside.write_text("Must not be used by this account.\n")
        (self.account / "company/profiles/alex/memory.md").symlink_to(outside)
        self.assertIn("escapes", self.teams("resolve", "synthetic", "dba", success=False))
        self.assertEqual(outside.read_text(), "Must not be used by this account.\n")

    def test_room_subsets_and_advisors_come_only_from_the_definition(self):
        self.new("dba", "alex", ("sam", "cto"), "--advisor", "ciso",
                 "--facilitation", "contrarian")
        before = self.definition().read_bytes()
        room = json.loads(self.teams("resolve", "synthetic", "dba", "--attendee", "sam",
                                     "--attendee", "ciso"))
        self.assertEqual(room["leader"]["profile"], "alex")
        self.assertEqual([p["profile"] for p in room["participants"]], ["sam", "ciso"])
        self.assertTrue(room["participants"][0]["vote"])
        self.assertFalse(room["participants"][1]["vote"])
        self.assertEqual(room["facilitation"], ["contrarian"])
        self.assertEqual(self.definition().read_bytes(), before)
        whole = json.loads(self.teams("resolve", "synthetic", "dba"))
        self.assertFalse(whole["participants"][-1]["vote"])
        for option in (("--attendee", "alex"), ("--attendee", "unknown"),
                       ("--attendee", "coo"), ("--attendee", "sam", "--attendee", "sam")):
            with self.subTest(option=option):
                self.teams("resolve", "synthetic", "dba", *option, success=False)

    def test_question_guest_override_is_rejected_without_changing_the_team(self):
        self.new()
        before = self.definition().read_bytes()
        result = subprocess.run(
            ["python3", "scripts/teams.py", "resolve", "synthetic", "dba", "--guest", "ciso"],
            cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --guest ciso", result.stderr)
        self.assertEqual(self.definition().read_bytes(), before)

    def test_invalid_definitions_fail_explicitly(self):
        self.new()
        valid = json.loads(self.definition().read_text())
        cases = [
            [],
            {**valid, "leader": None},
            {**valid, "leader": "absent"},
            {**valid, "participants": []},
            {**valid, "participants": [{"profile": "alex"}]},
            {**valid, "participants": [{"profile": "sam"}, {"profile": "sam"}]},
            {**valid, "participants": [{"profile": "sam", "vote": "yes"}]},
            {**valid, "participants": [{"profile": "../other"}]},
            {**valid, "facilitation": ["contrarian", "contrarian"]},
            {**valid, "facilitation": ["cfo"]},
            {**valid, "purpose": "TBD"},
            {**valid, "escalates_to": []},
            {**valid, "typo": True},
        ]
        for definition in cases:
            with self.subTest(definition=definition):
                self.rewrite(definition)
                self.teams("check", "synthetic", "dba", success=False)
        self.definition().write_text("{")
        self.teams("resolve", "synthetic", "dba", success=False)

    def test_invalid_creation_does_not_leave_a_partial_team(self):
        self.teams("new", "synthetic", "bad", "--leader", "alex",
                   "--participant", "absent", "--purpose", "Test", success=False)
        self.assertFalse((self.account / "teams/bad").exists())
        self.new()
        before = self.definition().read_bytes()
        self.teams("new", "synthetic", "dba", "--leader", "sam", "--participant", "alex",
                   "--purpose", "Replacement", success=False)
        self.assertEqual(self.definition().read_bytes(), before)

    def test_thin_profiles_warn_without_fabrication_or_blocking(self):
        self.new("core", "leader", ("cfo",))
        room = json.loads(self.teams("resolve", "synthetic", "core"))
        self.assertTrue(room["warnings"])
        self.assertEqual(room["leader"]["name"], "Generic CEO")
        self.assertIn("profile warnings", self.teams("check", "synthetic", "core"))

    def test_cross_account_paths_and_symlinked_profiles_are_rejected(self):
        self.new()
        self.run_script("accounts", "new", "other")
        alias = self.account / "company/profiles/outsider"
        alias.symlink_to(self.root / "accounts/other/company/profiles/cfo", target_is_directory=True)
        valid = json.loads(self.definition().read_text())
        self.rewrite({**valid, "leader": "outsider"})
        self.assertIn("escapes", self.teams("resolve", "synthetic", "dba", success=False))
        self.teams("list", "../other", success=False)
        self.teams("resolve", "synthetic", "../other", success=False)
        (self.account / "teams/outside").symlink_to(self.root / "accounts/other",
                                                    target_is_directory=True)
        self.assertIn("escapes", self.teams("resolve", "synthetic", "outside", success=False))
        (self.root / "accounts/alias").symlink_to(self.root / "accounts/other",
                                                 target_is_directory=True)
        self.assertIn("must not be a symlink", self.teams("list", "alias", success=False))

    def test_transcript_retains_resolved_room_after_membership_changes(self):
        self.new("dba", "alex", ("sam",), "--advisor", "ciso", "--facilitation", "contrarian")
        room = json.loads(self.teams("resolve", "synthetic", "dba"))
        transcript = {
            "session": {**room, "topic": "Synthetic", "date": "2026-11-17",
                        "leader": room["leader"]["profile"], "deliberation_rounds": 4},
            "turns": [{"speaker": "ciso", "round": "briefing", "position": None,
                       "content": "Advisor briefing verbatim."},
                      {"speaker": "sam", "round": "opening", "content": "Original argument."},
                      {"speaker": "ciso", "round": "final_vote", "position": None,
                       "content": "Keep the safeguard."}],
            "final_votes": [{"speaker": "sam", "position": "SUPPORT", "reason": "Capacity"}],
            "archetype_positions": [{"speaker": "contrarian", "position": "CONDITIONAL",
                                    "reason": "Test failure modes"}],
            "decision": {"position": "SUPPORT", "rationale": "Synthetic decision"},
        }
        source = self.account / "teams/dba/decisions/synthetic-transcript.json"
        source.write_text(json.dumps(transcript))
        before = source.read_bytes()
        definition = json.loads(self.definition().read_text())
        definition["participants"] = [{"profile": "cto"}]
        self.rewrite(definition)
        self.run_script("render_transcript", str(source))
        rendered = source.with_name("synthetic-discussion.md").read_text()
        self.assertIn("simulation of Dba", rendered)
        self.assertIn("Sam Example (Database Engineer)", rendered)
        self.assertIn("**Leader:** Alex Example (DBA Lead)", rendered)
        self.assertIn("Original argument.", rendered)
        self.assertIn("## Advisor briefing", rendered)
        self.assertIn("Advisor briefing verbatim.", rendered)
        self.assertIn("Keep the safeguard.", rendered)
        participant_table, synthetic_table = rendered.split(
            "## Synthetic perspectives (not participant votes)")
        self.assertIn("## Participant votes", participant_table)
        self.assertNotIn("| Contrarian |", participant_table)
        self.assertNotIn("| Ciso Example", participant_table)
        self.assertIn("| Contrarian | CONDITIONAL |", synthetic_table)
        self.assertEqual(source.read_bytes(), before)
