#!/usr/bin/env python3
"""Tauri UI용 persistent JSON-lines WAAPI sidecar."""

import csv
import json
import os
import sys
from pathlib import Path

from auditor_constants import EXCEPTIONS_FILE, FIND_CMD_PRIMARY, WAAPI_URL, VERSION
from auditor_core import SCOPE_TREE_TYPES, audit_objects, effective_type

try:
    from waapi import WaapiClient
except ImportError:
    WaapiClient = None


class AuditorBackend:
    ROOT_PATH = "\\Actor-Mixer Hierarchy"
    CONTAINER_QUERY_TYPES = [
        "ActorMixer",
        "RandomSequenceContainer",
        "BlendContainer",
        "SwitchContainer",
    ]
    RETURN_FIELDS = [
        "id",
        "name",
        "path",
        "type",
        "workunit",
        "@OverridePositioning",
        "@ListenerRelativeRouting",
        "@3DSpatialization",
        "@Attenuation",
        "@EnableAttenuation",
    ]

    def __init__(self, exceptions_file=EXCEPTIONS_FILE):
        self.client = None
        self.project_name = ""
        self.find_command = None
        self.results = []
        self.total_checked = 0
        self.exceptions_file = Path(exceptions_file)
        self.exceptions = self._load_exceptions()

    def _object_get(self, from_clause, *, transform=None, return_fields=None):
        payload = {
            "from": from_clause,
            "options": {"return": return_fields or self.RETURN_FIELDS},
        }
        if transform:
            payload["transform"] = transform
        return self._require_client().call("ak.wwise.core.object.get", payload) or {}

    def _waql_get(self, query, *, return_fields=None):
        return (
            self._require_client().call(
                "ak.wwise.core.object.get",
                {"waql": query},
                options={"return": return_fields or self.RETURN_FIELDS},
            )
            or {}
        )

    @staticmethod
    def _waql_string(value):
        return '"' + str(value).replace('"', '\\"') + '"'

    def _load_exceptions(self):
        try:
            if self.exceptions_file.exists():
                return json.loads(self.exceptions_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _save_exceptions(self):
        self.exceptions_file.write_text(
            json.dumps(self.exceptions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _require_client(self):
        if self.client is None:
            raise RuntimeError("Wwise에 연결되지 않았습니다.")
        return self.client

    def ping(self, _payload):
        return {"version": VERSION, "backend": "python", "ready": True}

    def connect(self, _payload):
        if WaapiClient is None:
            raise RuntimeError("waapi-client가 설치되지 않았습니다. install.bat을 실행하세요.")
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
        self.client = WaapiClient(url=WAAPI_URL)
        self.find_command = None
        response = self.client.call(
            "ak.wwise.core.object.get",
            {"from": {"ofType": ["Project"]}, "options": {"return": ["name"]}},
        )
        projects = (response or {}).get("return", [])
        self.project_name = projects[0].get("name", "—") if projects else "—"
        return {
            "connected": True,
            "projectName": self.project_name,
            "exceptionCount": len(self.exceptions),
        }

    def status(self, _payload):
        if self.client is None:
            return {"connected": False, "projectName": ""}
        try:
            self.client.call("ak.wwise.core.getInfo")
            return {"connected": True, "projectName": self.project_name}
        except Exception:
            self.client = None
            self.project_name = ""
            return {"connected": False, "projectName": ""}

    def scope_children(self, payload):
        path = payload.get("path") or self.ROOT_PATH
        response = self._object_get(
            {"path": [path]},
            transform=[{"select": ["children"]}],
            return_fields=["id", "name", "path", "type", "filePath"],
        )
        children = []
        for obj in (response or {}).get("return", []):
            obj_type = effective_type(obj)
            if obj_type not in SCOPE_TREE_TYPES:
                continue
            children.append(
                {
                    "id": obj.get("id", ""),
                    "name": obj.get("name", ""),
                    "path": obj.get("path", ""),
                    "type": obj_type,
                    "expandable": True,
                }
            )
        return {"path": path, "children": children}

    def _ancestor_paths(self, path):
        ancestors = []
        current = path
        while True:
            separator = current.rfind("\\")
            if separator <= 0:
                break
            current = current[:separator]
            ancestors.append(current)
        return ancestors

    def _fetch_scan_objects(self, scope_paths, *, include_sounds, include_containers):
        """스캔 대상 타입만 WAQL로 가져오고 effective 판정용 조상을 보강한다."""
        roots = list(dict.fromkeys(scope_paths or [self.ROOT_PATH]))
        return_fields = [*self.RETURN_FIELDS, "filePath"]
        objects_by_path = {}
        target_types = []
        if include_sounds:
            target_types.append("Sound")
        if include_containers:
            target_types.extend(self.CONTAINER_QUERY_TYPES)
        type_clause = " or ".join(
            f"type = {self._waql_string(object_type)}" for object_type in target_types
        )

        for root in roots:
            for obj in self._object_get({"path": [root]}, return_fields=return_fields).get(
                "return", []
            ):
                if obj.get("path"):
                    objects_by_path[obj["path"]] = obj
            query = (
                f"$ from object {self._waql_string(root)} "
                f"select descendants where {type_clause}"
            )
            for obj in self._waql_get(query, return_fields=return_fields).get(
                "return", []
            ):
                if obj.get("path"):
                    objects_by_path[obj["path"]] = obj

        missing_ancestors = []
        seen = set(objects_by_path)
        for path in list(objects_by_path):
            for ancestor in self._ancestor_paths(path):
                if ancestor not in seen:
                    seen.add(ancestor)
                    missing_ancestors.append(ancestor)

        for start in range(0, len(missing_ancestors), 128):
            batch = missing_ancestors[start : start + 128]
            for obj in self._object_get({"path": batch}, return_fields=return_fields).get(
                "return", []
            ):
                if obj.get("path"):
                    objects_by_path[obj["path"]] = obj

        return list(objects_by_path.values())

    def scan(self, payload):
        include_sounds = bool(payload.get("includeSounds", True))
        include_containers = bool(payload.get("includeContainers", True))
        if not include_sounds and not include_containers:
            raise ValueError("오브젝트 타입을 하나 이상 선택하세요.")
        scope_paths = payload.get("scopePaths") or []
        all_objects = self._fetch_scan_objects(
            scope_paths,
            include_sounds=include_sounds,
            include_containers=include_containers,
        )
        audited = audit_objects(
            all_objects,
            include_sounds=include_sounds,
            include_containers=include_containers,
            scope_paths=scope_paths,
            exceptions=self.exceptions,
        )
        self.results = audited["results"]
        self.total_checked = audited["totalChecked"]
        if audited["invalidated"]:
            self.exceptions = audited["exceptions"]
            self._save_exceptions()
        return {
            "results": self.results,
            "totalChecked": self.total_checked,
            "exceptions": list(self.exceptions.values()),
            "invalidated": audited["invalidated"],
        }

    def get_exceptions(self, _payload):
        return {"exceptions": list(self.exceptions.values())}

    def add_exceptions(self, payload):
        selected_ids = set(payload.get("ids") or [])
        remaining = []
        for result in self.results:
            object_id = result.get("id", "")
            if object_id not in selected_ids:
                remaining.append(result)
                continue
            self.exceptions[object_id] = {
                **result,
                "fp": [result["spat"], result["att"], result["issue"]],
            }
        self.results = remaining
        self._save_exceptions()
        return {
            "results": self.results,
            "exceptions": list(self.exceptions.values()),
            "totalChecked": self.total_checked,
        }

    def remove_exceptions(self, payload):
        for object_id in payload.get("ids") or []:
            self.exceptions.pop(object_id, None)
        self._save_exceptions()
        return {"exceptions": list(self.exceptions.values())}

    def select_in_wwise(self, payload):
        client = self._require_client()
        object_ids = payload.get("ids") or []
        if not object_ids:
            raise ValueError("선택된 오브젝트가 없습니다.")
        if self.find_command:
            try:
                client.call(
                    "ak.wwise.ui.commands.execute",
                    {"command": self.find_command, "objects": object_ids},
                )
            except Exception:
                self.find_command = None
        if not self.find_command:
            for command in FIND_CMD_PRIMARY:
                try:
                    client.call(
                        "ak.wwise.ui.commands.execute",
                        {"command": command, "objects": object_ids},
                    )
                    self.find_command = command
                    break
                except Exception:
                    continue
            else:
                raise RuntimeError("Wwise에서 오브젝트를 선택할 수 없었습니다.")
        try:
            client.call(
                "ak.wwise.ui.commands.execute",
                {"command": "Inspect", "objects": object_ids},
            )
        except Exception:
            pass
        return {"selected": object_ids}

    def export_csv(self, payload):
        raw_path = str(payload.get("path") or "").strip()
        if not raw_path:
            raise ValueError("저장 경로가 없습니다.")
        path = Path(raw_path)
        language = payload.get("language", "ko")
        headers = (
            ["에셋 이름", "타입", "3D 모드", "Attenuation", "위반 유형", "Work Unit", "전체 경로"]
            if language == "ko"
            else ["Asset Name", "Type", "3D Mode", "Attenuation", "Issue", "Work Unit", "Full Path"]
        )
        issue_labels = (
            {"miss": "Attenuation 미설정", "extra": "2D에 ATT 연결"}
            if language == "ko"
            else {"miss": "Missing Attenuation", "extra": "2D + ATT linked"}
        )
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for result in self.results:
                writer.writerow(
                    [
                        result["name"],
                        result["type"],
                        result["spat"],
                        result["att"],
                        issue_labels[result["issue"]],
                        result["wu"],
                        result["path"],
                    ]
                )
        return {"path": str(path), "count": len(self.results)}

    def dispatch(self, command, payload):
        handler = getattr(self, command, None)
        if handler is None or command.startswith("_"):
            raise ValueError(f"알 수 없는 명령: {command}")
        return handler(payload or {})


def run_protocol():
    backend = AuditorBackend()
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            response = {
                "id": request.get("id"),
                "ok": True,
                "data": backend.dispatch(request.get("command", ""), request.get("payload")),
            }
        except Exception as error:
            response = {
                "id": locals().get("request", {}).get("id"),
                "ok": False,
                "error": str(error),
            }
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_protocol()
