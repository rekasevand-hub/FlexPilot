#!/usr/bin/env python3
"""在 Low-code platform 服务器上执行文件（支持路径映射，微流走运行时地址）"""
import argparse
import json
import logging
import os
import re
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
UTILS_DIR = SKILL_DIR / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))

import utils
import path_mapping


def resolve_local_path(local_file_path: Path, project_root: Path) -> Path:
    """优先使用用户传入的本地路径；不存在时兼容旧用法（src/xxx -> bzc/ 映射目录）"""
    if local_file_path.exists():
        return local_file_path
    remote_probe = path_mapping.convert_local_to_remote(local_file_path, project_root)
    alt = path_mapping.convert_remote_to_local(remote_probe, project_root)
    return alt if alt.exists() else local_file_path


def _repair_params_json(text: str) -> str:
    """修复 PowerShell 等外壳吞掉引号后的 JSON：'{flag: 0}' / {flag: 0} -> {"flag": 0}"""
    text = text.replace("'", '"')
    text = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', text)
    return text


def parse_params(params):
    """解析 --params：兼容 PowerShell 等外壳丢引号的情况"""
    if isinstance(params, dict):
        return params
    try:
        return json.loads(params)
    except (json.JSONDecodeError, ValueError):
        return json.loads(_repair_params_json(params))


def execute_remote_file(base_url: str, token_info, local_file_path: Path, project_root: Path,
                        method: str = 'main', params: str = '{}', debug: bool = False):
    local_file_path = resolve_local_path(local_file_path, project_root)
    if not local_file_path.exists():
        raise FileNotFoundError(f"本地文件不存在: {local_file_path}")

    remote_file_path = path_mapping.convert_local_to_remote(local_file_path, project_root)
    logger.info(f"本地路径: {local_file_path} -> Low-code platform 路径: {remote_file_path}")

    if utils.is_microflow(remote_file_path):
        return execute_microflow(base_url, token_info, remote_file_path, params, debug=debug)

    execute_url = utils.build_execute_url(base_url, remote_file_path)
    logger.info(f"执行 URL: {execute_url}")

    file_content = local_file_path.read_text(encoding='utf-8')
    file_ext = local_file_path.suffix.lower()
    file_type = utils.get_file_type(file_ext)

    if file_type == 'unknown':
        raise ValueError(f"不支持的文件类型: {file_ext}")

    uri_without_ext = f"/repository/{utils.strip_resource_extension(remote_file_path)}".replace('\\', '/')

    body = {
        'uri': uri_without_ext,
        'type': file_type,
        'code': file_content,
        'method': method,
        'params': parse_params(params),
    }

    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_info.bearerToken}'}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    body_bytes = json.dumps(body).encode('utf-8')

    try:
        req = urllib.request.Request(execute_url, data=body_bytes, headers=headers, method='PUT')
        response = urllib.request.urlopen(req, timeout=30, context=ctx)
        logger.info(f"执行成功: {response.status}")
    except urllib.error.HTTPError as exc:
        logger.error(f"执行失败: {exc}")
        raise

    console_output = response.headers.get('console', '')
    try:
        console_output = console_output.encode('latin-1').decode('utf-8')
    except UnicodeDecodeError:
        pass

    try:
        console_array = json.loads(console_output)
        if isinstance(console_array, list):
            formatted_console = '\n'.join(str(item) for item in console_array)
        else:
            formatted_console = console_output
    except (json.JSONDecodeError, ValueError):
        formatted_console = console_output

    result_data = json.loads(response.read().decode('utf-8'))
    return {'console': formatted_console, 'result': result_data, 'status_code': response.status}


def execute_microflow(base_url: str, token_info, file_path: str, params: str = '{}', debug: bool = False):
    """执行微流：PUT 到运行时地址（无 /repository 前缀），body 直接传微流入参"""
    execute_url = utils.build_microflow_url(base_url, file_path, debug=debug)
    logger.info(f"执行微流 URL: {execute_url}")

    body = parse_params(params)
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_info.bearerToken}'}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    body_bytes = json.dumps(body).encode('utf-8')

    try:
        req = urllib.request.Request(execute_url, data=body_bytes, headers=headers, method='PUT')
        response = urllib.request.urlopen(req, timeout=180, context=ctx)
        logger.info(f"执行成功: {response.status}")
    except urllib.error.HTTPError as exc:
        logger.error(f"执行失败: {exc}")
        raise

    result_data = json.loads(response.read().decode('utf-8'))
    return {'console': '', 'result': result_data, 'status_code': response.status}


def main():
    parser = argparse.ArgumentParser(description='在 Low-code platform 服务器上执行文件')
    utils.add_common_args(parser)
    parser.add_argument('--file', type=str, required=True, help='文件路径 (相对于 src/ 或 bzc/)')
    parser.add_argument('--method', type=str, default='main', help='执行的方法 (默认: main)')
    parser.add_argument('--params', type=str, default='{}', help='JSON 参数')

    args = parser.parse_args()
    utils.setup_logging(args.debug)
    global logger
    logger = logging.getLogger(__name__)

    if args.proxy:
        os.environ['HTTP_PROXY'] = f'http://{args.proxy}:{args.port}'
        os.environ['HTTPS_PROXY'] = f'http://{args.proxy}:{args.port}'

    account = utils.get_account_config(args.env)
    base_url = urlparse(account['url']).scheme + '://' + urlparse(account['url']).netloc
    logger.info(f"目标环境: {args.env}, Base URL: {base_url}")

    project_root = utils.find_project_root()
    local_file_path = Path(args.file)
    if not local_file_path.is_absolute():
        local_file_path = project_root / local_file_path

    token_info = utils.get_flexpilot_token(
        base_url, account['user'], account['password'], account['org'], account.get('tokenUri')
    )

    try:
        result = execute_remote_file(base_url, token_info, local_file_path, project_root, args.method, args.params, args.debug)
    except Exception as exc:
        logger.error(f"执行失败: {exc}")
        return 1

    print('=' * 25 + ' 执行结果 ' + '=' * 25)
    if result['console']:
        print(f"控制台输出:\n{result['console']}\n")
    print('-' * 50)
    print(f"返回:\n{json.dumps(result['result'], indent=2, ensure_ascii=False)}")
    print('-' * 50)
    print(f"状态码: {result['status_code']}")

    data = result['result']
    if isinstance(data, dict):
        debug = data.get('debug') or {}
        if debug.get('error'):
            logger.error(f"执行失败: {debug['error']}")
            return 1
        if data.get('error') and data['error'] != 'SUCCESS':
            logger.error(f"执行失败: {data['error']}")
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
