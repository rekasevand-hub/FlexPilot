#!/usr/bin/env python3
"""Low-code platform 路径映射工具"""
from pathlib import Path

REMOTE_TO_LOCAL = {
    'mold_manage/bzcomponent': 'bzc/模具管理',
    'interface_manage/bzcomponent': 'bzc/接口管理',
    'oee/bzcomponent': 'bzc/OEE展示',
    'base/bzcomponent': 'bzc/基础',
    'quality/bzcomponent': 'bzc/生产管理/单据记录/产品质量批量问题记录',
}

LOCAL_TO_REMOTE = {v: k for k, v in REMOTE_TO_LOCAL.items()}

def _normalize_path(path: str) -> str:
    return path.replace('\\', '/').replace('//', '/')

def convert_remote_to_local(remote_path: str, project_root: Path) -> Path:
    remote_path = _normalize_path(remote_path)

    for remote_prefix, local_prefix in REMOTE_TO_LOCAL.items():
        if remote_path.startswith(remote_prefix):
            relative_path = remote_path[len(remote_prefix):].lstrip('/')
            if relative_path:
                return project_root / local_prefix / relative_path
            else:
                return project_root / local_prefix

    if remote_path.startswith('src/'):
        return project_root / remote_path

    return project_root / 'bzc' / remote_path

def convert_local_to_remote(local_path: Path, project_root: Path) -> str:
    local_path_str = _normalize_path(str(local_path))
    project_root_str = _normalize_path(str(project_root))

    if local_path_str.startswith(project_root_str):
        local_path_str = local_path_str[len(project_root_str):].lstrip('/')

    for local_prefix, remote_prefix in LOCAL_TO_REMOTE.items():
        normalized_prefix = _normalize_path(local_prefix)
        if local_path_str == normalized_prefix or local_path_str.startswith(normalized_prefix + '/'):
            suffix = local_path_str[len(normalized_prefix):].lstrip('/')
            if suffix:
                return remote_prefix + '/' + suffix
            return remote_prefix

    if local_path_str.startswith('src/'):
        return local_path_str[4:].lstrip('/')

    return local_path_str