import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


class RetiredAccountGuardTests(unittest.TestCase):
    def test_cached_hook_is_inert_even_with_invalid_input_and_legacy_locks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "scripts/account_guard.py"
            script.parent.mkdir()
            shutil.copyfile(SOURCE / "scripts/account_guard.py", script)
            state = root / ".copilot/account-locks"
            state.mkdir(parents=True)
            legacy = state / "previous-session"
            legacy.write_text("unrelated-account")
            for payload in ("not JSON", json.dumps({
                "sessionId": "old-session", "toolName": "rg",
                "toolArgs": {"pattern": "example"}
            })):
                with self.subTest(payload=payload):
                    result = subprocess.run(["python3", str(script)], input=payload,
                                            cwd=root, text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(result.stderr, "")
            self.assertEqual(list(state.iterdir()), [legacy])
            self.assertEqual(legacy.read_text(), "unrelated-account")
