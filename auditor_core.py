"""UI와 독립된 Attenuation 감사 규칙.

이 모듈은 Tkinter 앱과 Tauri sidecar가 동일한 판정 계약을 공유하기 위한
순수 함수 모음이다. WAAPI 연결이나 파일 I/O를 포함하지 않는다.
"""

CONTAINER_TYPES = {
    "ActorMixer",
    "RandomSequenceContainer",
    "BlendContainer",
    "SwitchContainer",
}

SCOPE_TREE_TYPES = {
    "WorkUnit",
    "PhysicalFolder",
    "ActorMixer",
    "RandomSequenceContainer",
    "BlendContainer",
    "SwitchContainer",
    "Folder",
}

SPAT_LABELS = {
    0: "None",
    1: "Position",
    2: "Position + Orientation",
}


def effective_type(obj):
    """WAAPI의 WorkUnit/PhysicalFolder 중복 타입을 filePath로 구분한다."""
    obj_type = obj.get("type", "")
    if obj_type == "WorkUnit":
        file_path = obj.get("filePath", "") or ""
        if not file_path.lower().endswith(".wwu"):
            return "PhysicalFolder"
    return obj_type


def matches_scope(path, scope_paths):
    if not scope_paths:
        return True
    return any(path == scope or path.startswith(scope + "\\") for scope in scope_paths)


def resolve_effective(path, obj_map, cache):
    """OverridePositioning=true인 가장 가까운 조상(자기 자신 포함)을 찾는다."""
    chain = []
    current = path
    while True:
        if current in cache:
            result = cache[current]
            for cached_path in chain:
                cache[cached_path] = result
            return result

        obj = obj_map.get(current)
        if obj:
            override = obj.get("@OverridePositioning")
            # Folder/WorkUnit처럼 키가 없는 노드는 건너뛴다. 구버전 WAAPI에서
            # positioning 속성만 반환되는 경우는 기존 앱의 호환 규칙을 유지한다.
            if override is True or (
                override is None and "@ListenerRelativeRouting" in obj
            ):
                for cached_path in chain + [current]:
                    cache[cached_path] = obj
                return obj

        chain.append(current)
        separator = current.rfind("\\")
        if separator <= 0:
            break
        current = current[:separator]

    for cached_path in chain:
        cache[cached_path] = None
    return None


def audit_objects(
    all_objects,
    *,
    include_sounds=True,
    include_containers=True,
    scope_paths=None,
    exceptions=None,
):
    """WAAPI object 목록을 감사하고 UI에 독립적인 결과를 반환한다.

    핵심 계약:
    - 3D = ListenerRelativeRouting AND 3DSpatialization in {1, 2}
    - 실효 ATT = EnableAttenuation AND Attenuation.name
    - miss = 3D AND NOT 실효 ATT
    - extra = 2D AND 실효 ATT
    """
    selected_scopes = set(scope_paths or [])
    exception_map = dict(exceptions or {})
    object_map = {obj["path"]: obj for obj in all_objects if obj.get("path")}
    effective_cache = {}
    audit_types = set()
    if include_sounds:
        audit_types.add("Sound")
    if include_containers:
        audit_types.update(CONTAINER_TYPES)

    total_checked = sum(
        1
        for obj in all_objects
        if obj.get("type") in audit_types
        and matches_scope(obj.get("path", ""), selected_scopes)
    )

    results = []
    invalidated = []
    for obj in all_objects:
        obj_path = obj.get("path", "")
        if obj.get("type") not in audit_types or not matches_scope(
            obj_path, selected_scopes
        ):
            continue

        effective = resolve_effective(obj_path, object_map, effective_cache)
        if effective is None:
            continue

        listener_relative = effective.get("@ListenerRelativeRouting", False)
        spatialization = effective.get("@3DSpatialization", 0)
        is_3d = bool(listener_relative) and spatialization in {1, 2}

        attenuation_ref = effective.get("@Attenuation") or {}
        attenuation_name = (
            attenuation_ref.get("name", "")
            if isinstance(attenuation_ref, dict)
            else ""
        )
        attenuation_enabled = effective.get("@EnableAttenuation", False)
        attenuation_active = bool(attenuation_enabled) and bool(attenuation_name)

        if is_3d and not attenuation_active:
            issue = "miss"
        elif not is_3d and attenuation_active:
            issue = "extra"
        else:
            continue

        attenuation_label = attenuation_name if attenuation_name else "—"
        if attenuation_name and not attenuation_enabled:
            attenuation_label += "  (disabled)"
        spatialization_label = SPAT_LABELS.get(spatialization, str(spatialization))
        object_id = obj.get("id", "")
        fingerprint = [spatialization_label, attenuation_label, issue]

        if object_id in exception_map:
            if fingerprint == exception_map[object_id].get("fp", []):
                continue
            invalidated.append(object_id)
            del exception_map[object_id]

        workunit = obj.get("workunit") or {}
        workunit_name = workunit.get("name", "") if isinstance(workunit, dict) else ""
        results.append(
            {
                "id": object_id,
                "name": obj.get("name", ""),
                "type": obj.get("type", ""),
                "spat": spatialization_label,
                "att": attenuation_label,
                "issue": issue,
                "wu": workunit_name,
                "path": obj_path,
            }
        )

    return {
        "results": results,
        "totalChecked": total_checked,
        "exceptions": exception_map,
        "invalidated": invalidated,
    }
