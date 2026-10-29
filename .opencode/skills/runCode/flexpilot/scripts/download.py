#!/usr/bin/env python3
"""从 Low-code platform 服务器下载文件（支持路径映射）"""
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


def download_single_file(base_url: str, token_info, file_relative_path: str, project_root: Path) -> bool:
    remote_file_url = utils.build_remote_url(base_url, file_relative_path)
    logger.info(f"远程文件 URL: {remote_file_url}")

    try:
        remote_file_info = utils.get_remote_file_info(remote_file_url, token_info)
    except Exception as exc:
        logger.error(f"获取远程文件信息失败: {exc}")
        return False

    local_file_path = path_mapping.convert_remote_to_local(file_relative_path, project_root)
    logger.info(f"保存文件到: {local_file_path}")
    local_file_path.parent.mkdir(parents=True, exist_ok=True)

    file_ext = local_file_path.suffix.lower()

    try:
        file_content = utils.get_file_content_field(file_ext, remote_file_info)
    except ValueError as exc:
        logger.error(str(exc))
        return False

    if file_content is None:
        logger.error("文件内容为空")
        return False

    try:
        if file_ext == '.json':
            file_content = json.dumps(file_content, indent=4, ensure_ascii=False)
        local_file_path.write_text(file_content, encoding='utf-8')
        logger.info(f"文件保存成功: {local_file_path}")
        return True
    except Exception as exc:
        logger.error(f"保存文件失败: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description='从 Low-code platform 服务器下载文件')
    utils.add_common_args(parser)
    parser.add_argument('--file', type=str, help='单个文件路径 (相对于 src/)')
    parser.add_argument('--files-info', type=str, help='JSON 文件列表')

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

    files_to_download = []
    if args.files_info:
        try:
            files_config = json.loads(Path(args.files_info).read_text(encoding='utf-8'))
            files_to_download = [item['path'] for item in files_config.get('files', [])]
        except Exception as exc:
            logger.error(f"读取文件列表失败: {exc}")
            return 1
    elif args.file:
        files_to_download = [args.file]
    else:
        logger.error('需要提供 --file 或 --files-info 参数')
        return 1

    project_root = utils.find_project_root()
    success, failed = 0, 0
    for index, file_path in enumerate(files_to_download, start=1):
        logger.info(f"处理文件 {index}/{len(files_to_download)}: {file_path}")
        if download_single_file(base_url, token_info, file_path, project_root):
            success += 1
        else:
            failed += 1

    logger.info(f"下载完成. 成功: {success}, 失败: {failed}, 总计: {len(files_to_download)}")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())