import unittest

from auditor_core import audit_objects, effective_type, resolve_effective


ROOT = "\\Actor-Mixer Hierarchy\\Default Work Unit"


def positioning(path, *, lr, spat, enabled, attenuation=None):
    return {
        "id": path,
        "name": path.rsplit("\\", 1)[-1],
        "path": path,
        "type": "ActorMixer",
        "@OverridePositioning": True,
        "@ListenerRelativeRouting": lr,
        "@3DSpatialization": spat,
        "@EnableAttenuation": enabled,
        "@Attenuation": attenuation or {"id": "{00000000-0000-0000-0000-000000000000}"},
    }


def sound(path):
    return {
        "id": "sound-id",
        "name": path.rsplit("\\", 1)[-1],
        "path": path,
        "type": "Sound",
        "workunit": {"name": "Default Work Unit"},
        "@OverridePositioning": False,
    }


class AuditorCoreTests(unittest.TestCase):
    def test_spatialization_none_is_2d_even_when_lr_is_on(self):
        parent = positioning(ROOT, lr=True, spat=0, enabled=False)
        child = sound(ROOT + "\\River")
        audited = audit_objects([parent, child], include_containers=False)
        self.assertEqual(audited["results"], [])

    def test_3d_without_effective_attenuation_is_miss(self):
        parent = positioning(ROOT, lr=True, spat=1, enabled=True)
        child = sound(ROOT + "\\Bird")
        audited = audit_objects([parent, child], include_containers=False)
        self.assertEqual(audited["results"][0]["issue"], "miss")

    def test_2d_with_attenuation_is_extra(self):
        parent = positioning(
            ROOT,
            lr=False,
            spat=0,
            enabled=True,
            attenuation={"id": "att-id", "name": "Outdoor"},
        )
        child = sound(ROOT + "\\Music")
        audited = audit_objects([parent, child], include_containers=False)
        self.assertEqual(audited["results"][0]["issue"], "extra")

    def test_exception_fingerprint_is_preserved(self):
        parent = positioning(ROOT, lr=True, spat=2, enabled=False)
        child = sound(ROOT + "\\Vehicle")
        exception = {
            "sound-id": {
                "fp": ["Position + Orientation", "—", "miss"],
            }
        }
        audited = audit_objects(
            [parent, child], include_containers=False, exceptions=exception
        )
        self.assertEqual(audited["results"], [])
        self.assertFalse(audited["invalidated"])

    def test_nearest_override_wins(self):
        parent = positioning(ROOT, lr=True, spat=1, enabled=False)
        nested_path = ROOT + "\\Nested"
        nested = positioning(
            nested_path,
            lr=False,
            spat=0,
            enabled=True,
            attenuation={"id": "att-id", "name": "UI"},
        )
        child = sound(nested_path + "\\Click")
        result = resolve_effective(child["path"], {o["path"]: o for o in [parent, nested, child]}, {})
        self.assertEqual(result["path"], nested_path)

    def test_physical_folder_detection(self):
        self.assertEqual(effective_type({"type": "WorkUnit", "filePath": "Folder"}), "PhysicalFolder")
        self.assertEqual(effective_type({"type": "WorkUnit", "filePath": "Unit.wwu"}), "WorkUnit")


if __name__ == "__main__":
    unittest.main()
