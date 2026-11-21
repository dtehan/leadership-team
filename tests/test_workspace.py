import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


class SyntheticWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(SOURCE / "company-template", self.root / "company-template")

    def run_script(self, name, *args):
        result = subprocess.run(["python3", f"scripts/{name}.py", *args],
                                cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_account_team_and_index_helpers_share_profile_context(self):
        self.run_script("accounts", "new", "synthetic")
        self.run_script("teams", "new", "synthetic", "platform", "--leader", "cto",
                        "--participant", "coo", "--advisor", "cfo",
                        "--purpose", "Platform decisions")
        company = self.root / "accounts/synthetic/company"
        doc = company / "technical/test.md"
        doc.write_text("---\nsummary: Synthetic platform\nroles: [cto]\n---\n# Test\n")
        self.run_script("build_index", "synthetic")
        self.assertIn("Synthetic platform", (company / "technical/index.md").read_text())
        self.run_script("build_index", "synthetic", "--check")
        room = json.loads(self.run_script("teams", "resolve", "synthetic", "platform"))
        self.assertEqual(room["leader"]["profile"], "cto")
        self.assertEqual([p["profile"] for p in room["participants"]], ["coo", "cfo"])
        self.assertFalse(room["participants"][1]["vote"])
        self.assertFalse((self.root / "accounts/synthetic/teams/platform/memories").exists())
        self.assertEqual(room["leader"]["memory"], "company/profiles/cto/memory.md")
        self.assertEqual({p.name for p in (self.root / "accounts/synthetic").iterdir()},
                         {"company", "teams"})

    def test_specialist_dispatch_inherits_orchestrator_model(self):
        evaluate = (SOURCE / ".github/skills/evaluate/SKILL.md").read_text()
        instructions = (SOURCE / ".github/copilot-instructions.md").read_text()
        agent = (SOURCE / ".github/agents/leadership-specialist.agent.md").read_text()
        self.assertIn("Omit the `model` parameter", evaluate)
        self.assertIn("do not pin a model", evaluate.lower())
        self.assertIn("omit each specialist `model` parameter", instructions)
        self.assertIn("orchestrator's inherited session\nmodel", agent)
        self.assertNotIn("model:", agent)

    def test_account_setup_ignores_legacy_locks_and_needs_no_runtime_identity(self):
        state = self.root / ".copilot/account-locks"
        state.mkdir(parents=True)
        legacy = state / "previous-session"
        legacy.write_text("unrelated-account")
        self.run_script("accounts", "new", "synthetic")
        self.assertIn("synthetic", self.run_script("accounts", "list"))
        self.run_script("teams", "new", "synthetic", "platform", "--leader", "cto",
                        "--participant", "coo", "--purpose", "Platform decisions")
        room = json.loads(self.run_script("teams", "resolve", "synthetic", "platform"))
        self.assertEqual(room["account"], "synthetic")
        self.assertEqual(list(state.iterdir()), [legacy])
        self.assertEqual(legacy.read_text(), "unrelated-account")
        result = subprocess.run(["python3", "scripts/accounts.py", "lock", "synthetic"],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stderr)

    def test_transcript_without_a_named_team_fails_without_writing_a_discussion(self):
        source = self.root / "incomplete-transcript.json"
        source.write_text(json.dumps({"session": {"topic": "Synthetic"}, "turns": []}))
        before = source.read_bytes()
        result = subprocess.run(["python3", "scripts/render_transcript.py", str(source)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: Transcript session must specify team", result.stderr)
        self.assertFalse(source.with_name("incomplete-discussion.md").exists())
        self.assertEqual(source.read_bytes(), before)

    def test_transcript_requires_snapshotted_leader_identity(self):
        source = self.root / "incomplete-transcript.json"
        transcript = {"session": {"team": "platform", "team_name": "Platform",
                                  "leader": "alex", "roster": {"sam": "Sam Example"}},
                      "turns": []}
        source.write_text(json.dumps(transcript))
        result = subprocess.run(["python3", "scripts/render_transcript.py", str(source)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("display-name roster containing its leader", result.stderr)
        self.assertFalse(source.with_name("incomplete-discussion.md").exists())

    def complete_transcript(self):
        people = [{"profile": "sam", "vote": True}, {"profile": "ciso", "vote": False}]
        turns = [
            {"round": "opening", "speaker": "alex", "role": "facilitator", "content": "Frame the trade-off."},
            {"round": "briefing", "speaker": "ciso", "content": "Require a recovery plan."},
            {"round": "opening", "speaker": "alex", "content": "Start with a bounded trial."},
            {"round": "opening", "speaker": "sam", "content": "Capacity is constrained."},
            {"round": "opening", "speaker": "contrarian", "content": "Compare the alternative."},
        ]
        for number, speaker in enumerate(("sam", "ciso", "contrarian", "sam"), 1):
            turns.append({"round": "deliberation", "speaker": speaker,
                          "deliberation_round": number, "content": f"Challenge {number}."})
        turns.extend([
            {"round": "final_vote", "speaker": "sam", "position": "SUPPORT", "content": "Capacity secured."},
            {"round": "final_vote", "speaker": "ciso", "position": None, "content": "Keep the safeguard."},
            {"round": "final_vote", "speaker": "contrarian", "position": "CONDITIONAL",
             "content": "Keep the stop condition."},
        ])
        return {
            "session": {
                "team": "platform", "team_name": "Platform", "leader": "alex", "deliberation_rounds": 4,
                "team_snapshot": {"leader": "alex", "participants": people, "facilitation": ["contrarian"]},
                "effective_room": {"leader": {"profile": "alex"}, "participants": people,
                                   "facilitation": ["contrarian"]},
                "roster": {"alex": "Alex Example", "sam": "Sam Example", "ciso": "Security Advisor",
                           "contrarian": "Contrarian"},
            },
            "turns": turns,
            "final_votes": [{"speaker": "sam", "position": "SUPPORT", "reason": "Capacity secured"}],
            "archetype_positions": [{"speaker": "contrarian", "position": "CONDITIONAL",
                                    "reason": "Stop condition"}],
            "decision": {"position": "SUPPORT", "rationale": "Bounded trial with safeguards",
                         "vote_tally": {"support": 1, "oppose": 0, "conditional": 0}},
        }

    def test_completion_check_accepts_recorded_room_without_writing(self):
        source = self.root / "complete-transcript.json"
        transcript = self.complete_transcript()
        for uppercase in (False, True):
            with self.subTest(uppercase_tally=uppercase):
                if uppercase:
                    transcript["decision"]["vote_tally"] = {
                        key.upper(): value for key, value in transcript["decision"]["vote_tally"].items()}
                source.write_text(json.dumps(transcript))
                before = source.read_bytes()
                output = self.run_script("render_transcript", str(source), "--check")
                self.assertIn("Transcript complete:", output)
                self.assertEqual(source.read_bytes(), before)
                self.assertFalse(source.with_name("complete-discussion.md").exists())

    def test_evaluate_and_legacy_decision_workflows_render_identically(self):
        source = self.root / "evaluation-transcript.json"
        discussion = source.with_name("evaluation-discussion.md")
        expected = None
        for workflow in (None, "evaluate", "convene"):
            with self.subTest(workflow=workflow):
                transcript = self.complete_transcript()
                if workflow is not None:
                    transcript["session"]["workflow"] = workflow
                source.write_text(json.dumps(transcript))
                before = source.read_bytes()
                self.run_script("render_transcript", str(source), "--check")
                self.run_script("render_transcript", str(source))
                rendered = discussion.read_text()
                self.assertIn("## Decision", rendered)
                self.assertIn("## Participant votes", rendered)
                if expected is None:
                    expected = rendered
                self.assertEqual(rendered, expected)
                self.assertEqual(source.read_bytes(), before)

    def complete_brainstorm(self):
        t = self.complete_transcript()
        t["session"].update(workflow="brainstorm", refinement_rounds=2)
        for field in ("team_snapshot", "effective_room"):
            t["session"][field]["participants"] = [
                {"profile": "sam", "vote": True}, {"profile": "jo", "vote": True},
                {"profile": "ciso", "vote": False}]
        t["session"]["roster"]["jo"] = "Jo Example"
        t.update(framing="Generate options for reliability; compare impact, feasibility and evidence.",
                 decision=None, final_votes=[], archetype_positions=[])
        t["ideas"] = [
            {"id": f"idea-{i}", "title": f"Option {i}", "description": f"Mechanism {i}",
             "proposer": proposer, "assumptions": "Capacity unverified",
             "experiment": "Test one isolated workload"}
            for i, proposer in enumerate(("sam", "jo", "alex", "ciso", "contrarian"), 1)]
        t["turns"] = [
            {"round": "framing", "speaker": "alex", "role": "facilitator", "content": t["framing"]},
            {"round": "briefing", "speaker": "ciso", "content": "Protect recovery objectives."}]
        for idea in t["ideas"]:
            t["turns"].append({"round": "idea_generation", "speaker": idea["proposer"],
                               "content": idea["description"], "idea_ids": [idea["id"]]})
        for number, speakers in ((1, ("sam", "jo")), (2, ("ciso", "contrarian"))):
            for speaker in speakers:
                t["turns"].append({"round": "refinement", "speaker": speaker,
                                   "refinement_round": number, "content": "Develop the test and assumptions."})
        t["rankings"] = [
            {"speaker": "sam", "order": ["idea-1", "idea-2", "idea-3", "idea-4", "idea-5"],
             "reason": "Prefer the smallest valuable test."},
            {"speaker": "jo", "order": ["idea-2", "idea-1", "idea-3", "idea-4", "idea-5"],
             "reason": "Prefer reducing operational risk."}]
        for ranking in t["rankings"]:
            t["turns"].append({"round": "prioritization", **ranking, "content": ranking["reason"]})
        for speaker in ("ciso", "contrarian"):
            t["turns"].append({"round": "prioritization", "speaker": speaker,
                               "content": "Keep a recovery safeguard.", "position": None})
        t["prioritization"] = {
            "order": ["idea-2", "idea-1", "idea-3", "idea-4", "idea-5"],
            "rationale": "Explore two bounded tests; retain the remaining backlog.",
            "differences": "Break the first-place tie by operational risk.",
            "authority": "recommendation"}
        t["turns"].append({"round": "synthesis", "speaker": "alex", "role": "facilitator",
                           "content": t["prioritization"]["rationale"]})
        return t

    def test_brainstorm_check_and_render_preserve_rankings_backlog_and_ties(self):
        source = self.root / "ideas-brainstorm-transcript.json"
        t = self.complete_brainstorm()
        source.write_text(json.dumps(t))
        before = source.read_bytes()
        self.run_script("render_transcript", str(source), "--check")
        discussion = source.with_name("ideas-brainstorm-discussion.md")
        self.assertFalse(discussion.exists())
        self.run_script("render_transcript", str(source))
        output = discussion.read_text()
        self.assertIn("2 refinement rounds", output)
        self.assertIn("## Participant rankings (not approval votes)", output)
        self.assertIn("| idea-1 | 7 |", output)
        self.assertIn("| idea-2 | 7 |", output)
        self.assertIn("| idea-3 | 4 |", output)
        self.assertIn("| idea-4 | 2 |", output)
        self.assertIn("| idea-5 | 0 |", output)
        self.assertIn("Break the first-place tie", output)
        self.assertIn("not implementation approval", output)
        self.assertNotIn("## Decision", output)
        self.assertNotIn("## Participant votes", output)
        for idea in t["ideas"]:
            self.assertIn(f"### {idea['id']}: {idea['title']}", output)
        for turn in t["turns"]:
            self.assertIn(turn["content"], output)
        self.assertEqual(source.read_bytes(), before)

    def test_brainstorm_rejects_incomplete_or_ineligible_prioritization(self):
        cases = {}
        t = self.complete_brainstorm()
        t["rankings"].append({"speaker": "ciso", "order": t["rankings"][0]["order"], "reason": "Advisor"})
        cases["exactly voting participants"] = t
        t = self.complete_brainstorm()
        t["rankings"][0]["order"] = ["idea-1"] * 5
        cases["every idea once"] = t
        t = self.complete_brainstorm()
        t["turns"] = [turn for turn in t["turns"]
                      if not (turn["round"] == "refinement" and turn["speaker"] == "ciso")]
        cases["Missing refinement responses: ciso"] = t
        t = self.complete_brainstorm()
        t["session"]["refinement_rounds"] = 1
        cases["At least two numbered refinement rounds"] = t
        t = self.complete_brainstorm()
        t["turns"] = [turn for turn in t["turns"]
                      if not (turn["round"] == "prioritization" and turn["speaker"] == "jo")]
        cases["Missing prioritization responses: jo"] = t
        t = self.complete_brainstorm()
        t["turns"][-5]["reason"] = "Not the recorded reason."
        cases["inconsistent ranking response for sam"] = t
        t = self.complete_brainstorm()
        t["prioritization"]["differences"] = ""
        cases["tie-breaking"] = t
        t = self.complete_brainstorm()
        t["prioritization"]["order"].reverse()
        t["prioritization"]["differences"] = ""
        cases["ranking reversals"] = t
        t = self.complete_brainstorm()
        t["prioritization"]["order"].pop()
        cases["Missing full leader priorities"] = t
        t = self.complete_brainstorm()
        t["prioritization"]["authority"] = "approval"
        cases["exploration recommendation"] = t
        t = self.complete_brainstorm()
        t["ideas"][0]["proposer"] = "ciso"
        cases["proposal provenance for idea-1"] = t
        t = self.complete_brainstorm()
        t["turns"].insert(-1, {"round": "idea_generation", "speaker": "sam",
                              "content": "Late proposal.", "idea_ids": ["idea-1"]})
        cases["frozen before prioritization"] = t
        t = self.complete_brainstorm()
        t["turns"][-2]["order"] = t["rankings"][0]["order"]
        cases["must not submit ranking ballots"] = t
        t = self.complete_brainstorm()
        t["turns"][-1]["position"] = "SUPPORT"
        cases["must not carry approve/deny positions"] = t
        t = self.complete_brainstorm()
        for field in ("team_snapshot", "effective_room"):
            for p in t["session"][field]["participants"]:
                p["vote"] = False
        t["rankings"] = []
        cases["at least one voting participant"] = t
        source = self.root / "rejected-brainstorm-transcript.json"
        for message, transcript in cases.items():
            with self.subTest(message=message):
                source.write_text(json.dumps(transcript))
                before = source.read_bytes()
                result = subprocess.run(
                    ["python3", "scripts/render_transcript.py", str(source), "--check"],
                    cwd=self.root, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(source.read_bytes(), before)
                self.assertFalse(source.with_name("rejected-brainstorm-discussion.md").exists())

    def test_partial_brainstorm_renders_without_false_tallies(self):
        t = self.complete_brainstorm()
        t["session"].update(status="incomplete", incomplete_reason="Interrupted ranking")
        t["rankings"] = []
        source = self.root / "partial-brainstorm-transcript.json"
        source.write_text(json.dumps(t))
        self.run_script("render_transcript", str(source))
        output = source.with_name("partial-brainstorm-discussion.md").read_text()
        self.assertIn("not a completed brainstorm", output)
        self.assertIn("Recorded priorities (incomplete run)", output)
        self.assertNotIn("## Participant Borda totals", output)

    def test_brainstorm_rejects_malformed_fields_without_tracebacks(self):
        source = self.root / "malformed-brainstorm-transcript.json"
        for field, value, message in (
                ("workflow", "unknown", "workflow must be evaluate, brainstorm or scope"),
                ("idea_ids", None, "idea_ids must be a list"),
                ("rankings", [{"speaker": "sam", "order": [{}], "reason": "Bad ID"}],
                 "rankings must contain"),
                ("prioritization", {"order": None}, "prioritization must contain")):
            with self.subTest(field=field):
                t = self.complete_brainstorm()
                if field == "workflow":
                    t["session"][field] = value
                elif field == "idea_ids":
                    t["turns"][2][field] = value
                else:
                    t[field] = value
                source.write_text(json.dumps(t))
                result = subprocess.run(
                    ["python3", "scripts/render_transcript.py", str(source), "--check"],
                    cwd=self.root, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(source.with_name("malformed-brainstorm-discussion.md").exists())

    def complete_scope(self):
        t = self.complete_transcript()
        t["session"].update(workflow="scope", planning_rounds=2)
        t.update(
            source={"kind": "user_direction", "idea": "A bounded reliability pilot",
                    "reference": "user request", "basis": "Move forward and scope this pilot."},
            framing="Scope the pilot without assuming funding or delivery capacity.",
            decision=None, final_votes=[], archetype_positions=[],
            plan={
                "outcome": "More reliable workloads", "success_measures": "Agree a baseline and recovery target.",
                "in_scope": "One isolated workload", "out_of_scope": "Estate-wide migration",
                "deliverables": "Pilot evidence and recommendation", "assumptions": "Representative workload",
                "constraints": "Capacity unknown", "dependencies": "Access approval",
                "risks": "Pilot may not generalize", "open_questions": "Who funds the pilot?",
                "next_steps": "Request access and validate capacity", "dissent": "Advisor requires recovery evidence.",
                "rationale": "Limit exposure before broader change.", "authority": "recommendation",
                "readiness": "blocked",
                "phases": [{"name": "Pilot", "deliverable": "Recovery evidence",
                            "exit_criteria": "Recovery target demonstrated", "owner": "Proposed platform lead",
                            "timing": "Unknown until capacity confirmed", "dependencies": "Access approval"}]},
            blockers=[{"id": "blocker-1", "description": "Access approval missing",
                       "impact": "Cannot begin the pilot", "mitigation": "Use an isolated approved environment",
                       "owner": "Unknown; seek an access approver", "gate": "start",
                       "clearance": "Written access approval", "evidence": "No approval evidence supplied",
                       "status": "open"}],
            turns=[
                {"round": "framing", "speaker": "alex", "role": "facilitator",
                 "content": "Frame the selected pilot and authority."},
                {"round": "briefing", "speaker": "ciso", "content": "Access approval is missing.",
                 "blocker_ids": ["blocker-1"]}])
        for speaker in ("alex", "sam", "ciso", "contrarian"):
            t["turns"].append({"round": "scoping", "speaker": speaker,
                               "content": f"{speaker}: bound the pilot and define success."})
        for number, speakers in ((1, ("sam",)), (2, ("ciso", "contrarian"))):
            for speaker in speakers:
                t["turns"].append({"round": "planning", "speaker": speaker,
                                   "planning_round": number, "content": f"{speaker}: challenge dependencies."})
        for speaker in ("sam", "ciso", "contrarian"):
            t["turns"].append({"round": "plan_review", "speaker": speaker,
                               "content": f"{speaker}: keep access as a blocking gate."})
        t["turns"].append({"round": "synthesis", "speaker": "alex", "role": "facilitator",
                           "content": "The discussion is complete, but the plan remains blocked."})
        return t

    def test_scope_render_and_completion_distinguish_readiness_from_discussion(self):
        source = self.root / "pilot-scope-transcript.json"
        discussion = source.with_name("pilot-scope-discussion.md")
        for readiness in ("blocked", "conditional", "ready_for_review"):
            with self.subTest(readiness=readiness):
                t = self.complete_scope()
                t["plan"]["readiness"] = readiness
                if readiness == "conditional":
                    t["blockers"][0]["gate"] = "Pilot"
                elif readiness == "ready_for_review":
                    t["source"].update(kind="evaluate", reference="teams/platform/decisions/pilot-transcript.json",
                                       basis="Completed simulated SUPPORT decision; real funding remains unverified.")
                    t["blockers"][0].update(status="resolved", evidence="Supplied written access approval")
                source.write_text(json.dumps(t))
                before = source.read_bytes()
                self.run_script("render_transcript", str(source), "--check")
                self.run_script("render_transcript", str(source))
                rendered = discussion.read_text()
                self.assertIn(f"**Readiness:** {readiness}", rendered)
                self.assertIn("2 planning rounds", rendered)
                self.assertIn("## Scope and high-level plan", rendered)
                self.assertIn("## Blockers and mitigation strategies", rendered)
                self.assertIn(t["blockers"][0]["mitigation"], rendered)
                self.assertIn(t["blockers"][0]["clearance"], rendered)
                self.assertIn(t["blockers"][0]["owner"], rendered)
                self.assertIn(t["plan"]["phases"][0]["exit_criteria"], rendered)
                self.assertIn(t["plan"]["out_of_scope"], rendered)
                self.assertNotIn("## Decision", rendered)
                self.assertNotIn("## Participant votes", rendered)
                for turn in t["turns"]:
                    self.assertIn(turn["content"], rendered)
                self.assertEqual(source.read_bytes(), before)

    def test_scope_rejects_unrecorded_planning_and_inconsistent_blockers(self):
        cases = {}
        t = self.complete_scope()
        t.pop("source")
        cases["explicit evaluate or user-direction basis"] = t
        t = self.complete_scope()
        t["plan"]["readiness"] = "ready_for_review"
        cases["readiness must be blocked"] = t
        t = self.complete_scope()
        t["blockers"][0]["mitigation"] = ""
        cases["must include impact, mitigation"] = t
        t = self.complete_scope()
        t["blockers"][0]["gate"] = "Unlisted phase"
        cases["Unknown blocking gate"] = t
        t = self.complete_scope()
        t["blockers"][0]["status"] = "mitigated"
        cases["Invalid blocker status"] = t
        t = self.complete_scope()
        t["blockers"] = []
        cases["Raised blocker IDs must be retained"] = t
        t = self.complete_scope()
        t["turns"][1].pop("blocker_ids")
        cases["Missing recorded blocker provenance"] = t
        t = self.complete_scope()
        t["session"]["planning_rounds"] = 1
        cases["At least two numbered planning rounds"] = t
        t = self.complete_scope()
        t["turns"] = [turn for turn in t["turns"]
                      if not (turn["round"] == "planning" and turn["speaker"] == "ciso")]
        cases["Missing planning responses: ciso"] = t
        t = self.complete_scope()
        t["turns"] = [turn for turn in t["turns"]
                      if not (turn["round"] == "plan_review" and turn["speaker"] == "sam")]
        cases["Missing plan_review responses: sam"] = t
        t = self.complete_scope()
        t["turns"].insert(-1, {"round": "planning", "speaker": "sam", "planning_round": 3,
                              "content": "Material change after review."})
        t["session"]["planning_rounds"] = 3
        cases["review the plan after the last planning round"] = t
        t = self.complete_scope()
        t["turns"][-2]["position"] = "SUPPORT"
        cases["must not contain approval positions"] = t
        t = self.complete_scope()
        t["plan"]["authority"] = "decision"
        cases["recommendation, not implementation approval"] = t
        t = self.complete_scope()
        t["plan"]["phases"] = []
        cases["Missing complete scope"] = t
        t = self.complete_scope()
        t["plan"]["phases"][0]["exit_criteria"] = None
        cases["list of complete phases"] = t
        t = self.complete_scope()
        t["turns"][1]["blocker_ids"] = [None]
        cases["blocker_ids must be a list of text IDs"] = t
        source = self.root / "invalid-scope-transcript.json"
        for message, transcript in cases.items():
            with self.subTest(message=message):
                source.write_text(json.dumps(transcript))
                before = source.read_bytes()
                result = subprocess.run(
                    ["python3", "scripts/render_transcript.py", str(source), "--check"],
                    cwd=self.root, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(source.read_bytes(), before)
                self.assertFalse(source.with_name("invalid-scope-discussion.md").exists())

    def test_scope_supports_all_advisors_but_marks_partial_runs_explicitly(self):
        t = self.complete_scope()
        for field in ("team_snapshot", "effective_room"):
            t["session"][field]["participants"] = [
                {"profile": "sam", "vote": False}, {"profile": "ciso", "vote": False}]
        t["turns"].insert(2, {"round": "briefing", "speaker": "sam", "content": "Capacity is unknown."})
        source = self.root / "advisor-scope-transcript.json"
        source.write_text(json.dumps(t))
        self.run_script("render_transcript", str(source), "--check")
        t["session"].update(status="incomplete", incomplete_reason="Interrupted final review")
        t["turns"] = t["turns"][:3]
        source.write_text(json.dumps(t))
        self.run_script("render_transcript", str(source))
        rendered = source.with_name("advisor-scope-discussion.md").read_text()
        self.assertIn("not a completed scope", rendered)
        self.assertIn("Recorded scope and plan (incomplete run)", rendered)
        self.assertIn("Interrupted final review", rendered)

    def test_completion_check_rejects_missing_recording_and_false_completion(self):
        cases = {}
        t = self.complete_transcript()
        t["turns"] = []
        cases["No conversation turns"] = t
        t = self.complete_transcript()
        t["session"]["roster"] = {"alex": "Alex Example", "participants": "Three seats"}
        t["turns"] = []
        cases["Roster must name every effective seat"] = t
        t = self.complete_transcript()
        t["session"]["effective_room"]["participants"] = 3
        cases["Missing full effective room"] = t
        t = self.complete_transcript()
        t["turns"] = [turn for turn in t["turns"]
                      if not (turn["round"] == "deliberation" and turn["speaker"] == "ciso")]
        cases["Missing deliberation responses: ciso"] = t
        t = self.complete_transcript()
        t["turns"][5].pop("deliberation_round")
        cases["At least four numbered deliberation rounds"] = t
        t = self.complete_transcript()
        t["turns"] = [turn for turn in t["turns"] if turn["round"] != "final_vote"]
        cases["Missing final_vote responses"] = t
        t = self.complete_transcript()
        t["final_votes"].append({"speaker": "ciso", "position": "SUPPORT", "reason": "Not a voter"})
        cases["no leader or advisors"] = t
        t = self.complete_transcript()
        t["decision"]["vote_tally"]["conditional"] = 1
        cases["participant-only final votes"] = t
        t = self.complete_transcript()
        t["session"]["status"] = "incomplete"
        t["session"]["incomplete_reason"] = "Interrupted run"
        cases["Interrupted run"] = t
        source = self.root / "rejected-transcript.json"
        for message, transcript in cases.items():
            with self.subTest(message=message):
                source.write_text(json.dumps(transcript))
                before = source.read_bytes()
                result = subprocess.run(
                    ["python3", "scripts/render_transcript.py", str(source), "--check"],
                    cwd=self.root, text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(source.read_bytes(), before)
                self.assertFalse(source.with_name("rejected-discussion.md").exists())

    def test_partial_render_is_explicit_and_preserves_full_response(self):
        transcript = self.complete_transcript()
        content = "Opening evidence.\n\n" + " ".join(["Detailed reasoning."] * 100)
        transcript["turns"] = [{"round": "opening", "speaker": "sam", "content": content}]
        source = self.root / "partial-transcript.json"
        source.write_text(json.dumps(transcript))
        before = source.read_bytes()
        result = subprocess.run(["python3", "scripts/render_transcript.py", str(source)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING: Incomplete transcript", result.stderr)
        rendered = source.with_name("partial-discussion.md").read_text()
        self.assertIn("## Incomplete run", rendered)
        self.assertIn("not a completed team decision", rendered)
        self.assertIn("## Recorded recommendation (incomplete run)", rendered)
        self.assertIn(content, rendered)
        self.assertEqual(source.read_bytes(), before)

    def test_blank_response_is_rejected_without_writing(self):
        transcript = self.complete_transcript()
        transcript["turns"][0]["content"] = " \n"
        source = self.root / "blank-transcript.json"
        source.write_text(json.dumps(transcript))
        result = subprocess.run(["python3", "scripts/render_transcript.py", str(source)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nonempty content", result.stderr)
        self.assertFalse(source.with_name("blank-discussion.md").exists())

    def test_structured_framing_is_rejected_with_an_explicit_error(self):
        transcript = self.complete_transcript()
        transcript["framing"] = {"trade_off": "This must be text"}
        source = self.root / "framing-transcript.json"
        source.write_text(json.dumps(transcript))
        result = subprocess.run(["python3", "scripts/render_transcript.py", str(source)],
                                cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: Transcript framing must be text or null", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(source.with_name("framing-discussion.md").exists())
