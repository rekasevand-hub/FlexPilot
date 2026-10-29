#!/usr/bin/env python3
"""Low-code platform 工具类"""
import argparse
import base64
import hashlib
import json
import logging
import os
import re
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError


logger = logging.getLogger(__name__)

MAX_TOKEN_AGE = 1 * 60 * 60


class FlexPilotTokenInfo:
    def __init__(self, authToken: str, userToken: str = None, sessionId: str = None, bearerToken: str = None):
        self.authToken = authToken
        self.userToken = userToken
        self.sessionId = sessionId
        self.bearerToken = bearerToken or authToken


def find_project_root(start_dir: str = None) -> Path:
    start_path = Path(start_dir or os.getcwd()).resolve()
    for candidate in (start_path, *start_path.parents):
        accounts_file = candidate / '.opencode' / 'flexpilot-accounts.json'
        if accounts_file.exists():
            return candidate
    raise FileNotFoundError(
        f"未找到 flexpilot-accounts.json 文件\n"
        "请在项目根目录的 .opencode/ 目录下创建 flexpilot-accounts.json"
    )


def load_accounts(project_root: Path = None) -> dict:
    root = project_root or find_project_root()
    accounts_path = root / '.opencode' / 'flexpilot-accounts.json'
    if not accounts_path.exists():
        raise FileNotFoundError(
            f"账户配置文件不存在\n"
            "请在项目根目录的 .opencode/ 目录下创建 flexpilot-accounts.json"
        )
    with accounts_path.open('r', encoding='utf-8') as file:
        data = json.load(file)
        if 'environments' in data:
            return {env['name']: env for env in data['environments']}
        raise ValueError('无效的 flexpilot-accounts.json 格式，需要包含 environments 数组')


def get_account_config(env: str, project_root: Path = None) -> dict:
    accounts = load_accounts(project_root)
    if env not in accounts:
        available = ', '.join(accounts.keys())
        raise ValueError(f"未知环境 '{env}'，可用环境: {available}")
    return accounts[env]


def get_flexpilot_token(base_url: str, user: str, password: str, org: str, token_uri: str = None) -> FlexPilotTokenInfo:
    token_url = f'{base_url}/auth/login' if token_uri is None else token_uri
    token_url = re.sub(r'(?<!:)/{2,}', '/', token_url)  # 修正配置中可能出现的重复斜杠（如 //auth/login 会导致 401）
    logger.info(f'Token URL: {token_url}')

    body = json.dumps({'username': user, 'password': password, 'org': org}).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = request.Request(token_url, data=body, headers=headers, method='PUT')
        response = request.urlopen(req, timeout=30, context=ctx)
    except (URLError, HTTPError) as exc:
        logger.error(f"认证失败: {exc}")
        raise

    token_json = json.loads(response.read().decode('utf-8'))
    return FlexPilotTokenInfo(
        authToken=token_json.get('authToken'),
        userToken=token_json.get('userToken'),
        sessionId=token_json.get('sessionId'),
        bearerToken=token_json.get('bearerToken') or token_json.get('authToken'),
    )


def get_remote_file_info(url: str, token_info: FlexPilotTokenInfo) -> dict:
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_info.bearerToken}'}

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = request.Request(url, headers=headers, method='GET')
        response = request.urlopen(req, timeout=30, context=ctx)
        return json.loads(response.read().decode('utf-8'))
    except (URLError, HTTPError) as exc:
        logger.error(f'获取远程文件信息失败: {exc}')
        raise


def upload_remote_file_info(url: str, token_info: FlexPilotTokenInfo, file_info: dict) -> dict:
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token_info.bearerToken}'}
    body = json.dumps(file_info).encode('utf-8')

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = request.Request(url, data=body, headers=headers, method='PUT')
        response = request.urlopen(req, timeout=30, context=ctx)
        logger.info(f'文件上传成功: {response.status}')
        return json.loads(response.read().decode('utf-8'))
    except (URLError, HTTPError) as exc:
        logger.error(f'上传文件失败: {exc}')
        raise


def get_file_content_field(file_ext: str, file_info: dict) -> str:
    field_map = {'.groovy': 'content', '.html': 'view', '.js': 'frontController', '.json': 'content', '.sql': 'content'}
    file_ext = file_ext.lower()
    if file_ext not in field_map:
        raise ValueError(f'不支持的文件类型: {file_ext}')
    return file_info.get(field_map[file_ext])


def set_file_content_field(file_ext: str, file_info: dict, content: str) -> dict:
    field_map = {'.groovy': 'content', '.html': 'view', '.js': 'frontController', '.json': 'content', '.sql': 'content'}
    file_ext = file_ext.lower()
    if file_ext not in field_map:
        raise ValueError(f'不支持的文件类型: {file_ext}')
    field = field_map[file_ext]
    if file_ext == '.json':
        file_info[field] = json.loads(content)
    else:
        file_info[field] = content
    return file_info


def build_remote_url(base_url: str, file_relative_path: str) -> str:
    file_relative_path = file_relative_path.replace('\\', '/')
    if file_relative_path.startswith('src/'):
        remote_file_uri = os.path.relpath(file_relative_path, 'src')
    else:
        remote_file_uri = file_relative_path
    remote_file_uri = remote_file_uri.replace('\\', '/')  # Windows 下 os.path.relpath 返回反斜杠，需统一为正斜杠
    return f'{base_url}/repository/{os.path.splitext(remote_file_uri)[0]}?uiOnly=false'


def build_execute_url(base_url: str, file_relative_path: str) -> str:
    file_relative_path = file_relative_path.replace('\\', '/')
    if file_relative_path.startswith('src/'):
        remote_file_uri = os.path.relpath(file_relative_path, 'src')
    else:
        remote_file_uri = file_relative_path
    path_parts = remote_file_uri.split('/')
    module_name = path_parts[0] if path_parts else 'system'
    execute_url = f'{base_url}/{module_name}/service/developer/run/repository/{remote_file_uri}'
    execute_url = os.path.splitext(execute_url)[0]
    execute_url = execute_url.replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')
    return execute_url


def get_file_type(file_ext: str) -> str:
    type_map = {'.groovy': 'groovy', '.js': 'javascript', '.py': 'python'}
    return type_map.get(file_ext.lower(), 'unknown')


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument('--env', type=str, required=True, help='环境名，例如 dev 或 prod')
    parser.add_argument('--debug', action='store_true', help='启用调试日志')
    parser.add_argument('--proxy', type=str, default=None, help='代理 IP')
    parser.add_argument('--port', type=int, default=80, help='代理端口')