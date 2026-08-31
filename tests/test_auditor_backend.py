import csv
import tempfile
import unittest
from pathlib import Path

from auditor_backend import AuditorBackend


ROOT = "\\Actor-Mixer Hierarchy\\Default Work Unit"


class FakeClient:
    def __init__(self):
        self.commands = []
        self.object_get_calls = []

    def call(self, uri, args=None, **kwargs):
        args = args or {}
        if uri == "ak.wwise.core.object.get":
            self.object_get_calls.append(args)
        if (
            uri == "ak.wwise.core.object.get"
            and args.get("transform") == [{"select": ["children"]}]
        ):
            return {
                "return": [
                    {
                        "id": "wu-id",
                        "name": "Default Work Unit",
                        "path": ROOT,
                        "type": "WorkUnit",
                        "filePath": "Default Work Unit.wwu",
                    }
                ]
            }
        if uri == "ak.wwise.core.object.get" and "waql" in args:
            return {
                "return": [
                    {
                        "id": "parent-id",
                        "name": "Default Work Unit",
                        "path": ROOT,
                        "type": "ActorMixer",
                        "@OverridePositioning": True,
                        "@ListenerRelativeRouting": True,
                        "@3DSpatialization": 1,
                        "@EnableAttenuation": False,
                        "@Attenuation": {"id": "{00000000-0000-0000-0000-000000000000}"},
                    },
                    {
                        "id": "sound-id",
                        "name": "Bird",
                        "path": ROOT + "\\Bird",
                        "type": "Sound",
                        "workunit": {"name": "Default Work Unit"},
                        "@OverridePositioning": False,
                    },
                ]
            }
        if uri == "ak.wwise.core.object.get" and "path" in args.get("from", {}):
            paths = set(args["from"]["path"])
            return {
                "return": [
                    {
                        "id": "parent-id",
                        "name": "Default Work Unit",
                        "path": ROOT,
                        "type": "ActorMixer",
                        "@OverridePositioning": True,
                        "@ListenerRelativeRouting": True,
                        "@3DSpatialization": 1,
                        "@EnableAttenuation": False,
                        "@Attenuation": {"id": "{00000000-0000-0000-0000-000000000000}"},
                    }
                ]
                if ROOT in paths
                else []
            }
        if uri == "ak.wwise.ui.commands.execute":
            self.commands.append(args)
            return {}
        raise AssertionError(f"unexpected call: {uri} {args}")


class AuditorBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.exception_path = Path(self.temp.name) / "exceptions.json"
        self.backend = AuditorBackend(self.exception_path)
        self.backend.client = FakeClient()

    def test_scope_scan_exception_and_csv_workflow(self):
        scope = self.backend.scope_children({"path": "\\Actor-Mixer Hierarchy"})
        self.assertEqual(scope["children"][0]["type"], "WorkUnit")

        scan = self.backend.scan({"includeSounds": True, "includeContainers": False})
        self.assertEqual(scan["totalChecked"], 1)
        self.assertEqual(scan["results"][0]["issue"], "miss")
        self.assertTrue(
            any("where type = \"Sound\"" in call.get("waql", "") for call in self.backend.client.object_get_calls)
        )
        self.assertFalse(
            any("ofType" in call.get("from", {}) for call in self.backend.client.object_get_calls)
        )
        self.assertFalse(
            any(call.get("transform") == [{"select": ["descendants"]}] for call in self.backend.client.object_get_calls)
        )

        added = self.backend.add_exceptions({"ids": ["sound-id"]})
        self.assertEqual(added["results"], [])
        self.assertEqual(added["exceptions"][0]["fp"], ["Position", "—", "miss"])
        self.assertTrue(self.exception_path.exists())

        self.backend.results = scan["results"]
        csv_path = Path(self.temp.name) / "audit.csv"
        exported = self.backend.export_csv({"path": str(csv_path), "language": "ko"})
        self.assertEqual(exported["count"], 1)
        with csv_path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))
        self.assertEqual(rows[0][0], "에셋 이름")
        self.assertEqual(rows[1][4], "Attenuation 미설정")

        removed = self.backend.remove_exceptions({"ids": ["sound-id"]})
        self.assertEqual(removed["exceptions"], [])

    def test_select_in_wwise_uses_discovered_command(self):
        result = self.backend.select_in_wwise({"ids": ["sound-id"]})
        self.assertEqual(result["selected"], ["sound-id"])
        self.assertGreaterEqual(len(self.backend.client.commands), 2)

    def test_export_requires_a_path(self):
        with self.assertRaisesRegex(ValueError, "저장 경로"):
            self.backend.export_csv({"path": ""})


if __name__ == "__main__":
    unittest.main()
