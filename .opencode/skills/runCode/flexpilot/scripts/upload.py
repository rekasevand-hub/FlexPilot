#!/usr/bin/env python3
"""上传文件到 Low-code platform 服务器（支持路径映射）"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
UTILS_DIR = SKILL_DIR / "utils"
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))

import utils
import path_mapping


def check_remote_file_exists(base_url: str, remote_file_path: str, token_info) -> tuple:
    remote_file_url = utils.build_remote_url(base_url, remote_file_path)
    try:
        utils.get_remote_file_info(remote_file_url, token_info)
        return True, remote_file_url
    except Exception:
        return False, remote_file_url


def upload_single_file(base_url: str, token_info, local_file_path: Path, project_root: Path, force: bool = False) -> bool:
    logger.info(f"本地文件: {local_file_path}")

    if not local_file_path.exists():
        logger.error(f"文件不存在: {local_file_path}")
        return False

    remote_file_path = path_mapping.convert_local_to_remote(local_file_path, project_root)
    exists, remote_file_url = check_remote_file_exists(base_url, remote_file_path, token_info)

    if not exists:
        logger.error(f"远程文件不存在: {remote_file_url}")
        logger.error("请先在 Low-code platform 平台创建该文件后再上传")
        return False

    if not force:
        confirm = input(f"远程文件存在: {remote_file_url}\n确认上传? (y/n): ")
        if confirm.lower() != 'y':
            logger.info("已取消上传")
            return False

    logger.info(f"远程文件 URL: {remote_file_url}")

    try:
        remote_file_info = utils.get_remote_file_info(remote_file_url, token_info)
    except Exception as exc:
        logger.error(f"获取远程文件信息失败: {exc}")
        return False

    upload_file_info = remote_file_info.copy()

    try:
        file_content = local_file_path.read_text(encoding='utf-8')
        file_ext = local_file_path.suffix.lower()
        upload_file_info = utils.set_file_content_field(file_ext, upload_file_info, file_content)
        utils.upload_remote_file_info(remote_file_url, token_info, upload_file_info)
        logger.info(f"文件上传成功: {remote_file_url}")
        return True
    except Exception as exc:
        logger.error(f"上传文件失败: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description='上传文件到 Low-code platform 服务器')
    utils.add_common_args(parser)
    parser.add_argument('--file', type=str, help='单个文件路径 (相对于 bzc/ 或绝对路径)')
    parser.add_argument('--files-info', type=str, help='JSON 文件列表')
    parser.add_argument('--force', action='store_true', help='跳过确认直接上传')

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

    token_info = utils.get_flexpilot_token(
        base_url, account['user'], account['password'], account['org'], account.get('tokenUri')
    )

    project_root = utils.find_project_root()

    files_to_upload = []
    if args.files_info:
        try:
            files_config = json.loads(Path(args.files_info).read_text(encoding='utf-8'))
            files_to_upload = [Path(project_root) / item['path'] for item in files_config.get('files', [])]
        except Exception as exc:
            logger.error(f"读取文件列表失败: {exc}")
            return 1
    elif args.file:
        local_file_path = Path(args.file)
        if not local_file_path.is_absolute():
            local_file_path = project_root / args.file
        files_to_upload = [local_file_path]
    else:
        logger.error('需要提供 --file 或 --files-info 参数')
        return 1

    success, failed = 0, 0
    for index, file_path in enumerate(files_to_upload, start=1):
        logger.info(f"处理文件 {index}/{len(files_to_upload)}: {file_path}")
        if upload_single_file(base_url, token_info, file_path, project_root, args.force):
            success += 1
        else:
            failed += 1

    logger.info(f"上传完成. 成功: {success}, 失败: {failed}, 总计: {len(files_to_upload)}")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())