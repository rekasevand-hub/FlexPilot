/**
 * Qoder Repowiki → 项目根 wiki/ 同步脚本
 *
 * 功能：读取 .qoder/repowiki/zh/content/ 下所有 Markdown 文档，
 *      按原目录结构同步到项目根目录 wiki/，并生成 wiki/README.md 索引。
 *      让所有 AI 工具（Kimi Code / Codex / Opencode 等）都能直接引用知识库，
 *      而不仅仅局限于 Qoder 私有的 .qoder/repowiki 目录。
 *
 * 说明：.qoder/repowiki 由 Qoder 生成与维护（meta/ 为其内部元数据，不同步），
 *      本脚本只做单向分发，请勿手工编辑 wiki/ 下的文档。
 *
 * 用法：node sync-repowiki.js [--dry-run]
 *
 * 参数：
 *   --dry-run  只显示将要执行的操作，不实际写入文件
 */

const fs = require("fs");
const path = require("path");

// 项目根目录（脚本所在目录的上一级）
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.dirname(SCRIPT_DIR);

const SOURCE_DIR = path.join(PROJECT_ROOT, ".qoder", "repowiki", "zh", "content");
const TARGET_DIR = path.join(PROJECT_ROOT, "wiki");
const INDEX_FILE = path.join(TARGET_DIR, "README.md");

// 脱敏映射：同步到 wiki/ 时替换公司/平台标识符（源文件不动，防止 Qoder 重新生成后泄露）
const REDACTIONS = [
  [/cmesdev\.fiberhome\.com/g, "lowcode-dev.example.com"],
  [/cmesqasnew\.fiberhome\.com/g, "lowcode-qas.example.com"],
  [/cmes\.fiberhome\.com/g, "lowcode.example.com"],
  [/fiberhome/gi, "lowcode"],
  [/FlexWeaver/g, "Low-code platform"],
  [/flexweaver/g, "flexpilot"],
  [/RTDSoft/g, "Low-code platform"],
];

function redact(content) {
  let out = content;
  for (const [re, to] of REDACTIONS) out = out.replace(re, to);
  return out;
}

/**
 * 递归收集目录下所有 .md 文件（返回相对于 baseDir 的路径）
 */
function findMarkdownFiles(baseDir, prefix = "") {
  const files = [];
  for (const entry of fs.readdirSync(baseDir, { withFileTypes: true })) {
    const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
    const full = path.join(baseDir, entry.name);
    if (entry.isDirectory()) {
      files.push(...findMarkdownFiles(full, rel));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      files.push(rel);
    }
  }
  return files;
}

/**
 * 同步单个文件，返回状态（新建/更新/无变化）
 */
function syncFile(relPath, dryRun) {
  const source = path.join(SOURCE_DIR, relPath);
  const target = path.join(TARGET_DIR, relPath);

  const content = redact(fs.readFileSync(source, "utf-8"));

  let changed = true;
  let status;
  if (fs.existsSync(target)) {
    const existing = fs.readFileSync(target, "utf-8");
    if (existing === content) {
      changed = false;
      status = "无变化";
    } else {
      status = "更新";
    }
  } else {
    status = "新建";
  }

  if (dryRun || !changed) {
    console.log(`  [${status}] ${relPath}`);
    return status;
  }

  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content, "utf-8");
  console.log(`  [${status}] ${relPath}`);
  return status;
}

/**
 * 生成 wiki/README.md 索引
 */
function buildIndex(files) {
  const lines = [
    "# CMES 项目知识库",
    "",
    "> 本目录由 `scripts/sync-repowiki.js` 从 `.qoder/repowiki/zh/content/` 自动同步生成，",
    "> 请勿手工编辑；源文档更新后重新运行 `node scripts/sync-repowiki.js` 即可。",
    "",
    "AI 工具使用指引：先读 `项目概述.md` 建立整体认识，再按下表按需查阅具体文档。",
    "",
    "## 文档索引",
    "",
  ];

  // 按目录分组
  const groups = new Map();
  for (const rel of files.slice().sort()) {
    const dir = rel.includes("/") ? rel.slice(0, rel.lastIndexOf("/")) : "";
    if (!groups.has(dir)) groups.set(dir, []);
    groups.get(dir).push(rel);
  }

  for (const [dir, groupFiles] of [...groups.entries()].sort()) {
    if (dir) lines.push(`### ${dir}/`, "");
    for (const rel of groupFiles) {
      const name = path.basename(rel, ".md");
      lines.push(`- [${name}](${rel})`);
    }
    lines.push("");
  }

  return lines.join("\n");
}

/**
 * 主函数
 */
function main() {
  const dryRun = process.argv.includes("--dry-run");

  console.log("=".repeat(50));
  console.log("Qoder Repowiki → wiki/ 同步");
  console.log("=".repeat(50));

  if (!fs.existsSync(SOURCE_DIR)) {
    console.log(`错误：找不到源目录 ${SOURCE_DIR}`);
    process.exit(1);
  }

  if (dryRun) {
    console.log("（dry-run 模式，不实际写入文件）");
  }

  console.log(`\n源目录：${SOURCE_DIR}`);
  console.log(`目标目录：${TARGET_DIR}`);
  console.log();

  const files = findMarkdownFiles(SOURCE_DIR);
  console.log(`找到 ${files.length} 个文档：\n`);

  for (const rel of files.slice().sort()) {
    syncFile(rel, dryRun);
  }

  // 生成索引
  const index = buildIndex(files);
  if (dryRun) {
    console.log(`\n  [索引] README.md（${files.length} 个条目）`);
  } else {
    const existing = fs.existsSync(INDEX_FILE) ? fs.readFileSync(INDEX_FILE, "utf-8") : null;
    if (existing !== index) {
      fs.mkdirSync(TARGET_DIR, { recursive: true });
      fs.writeFileSync(INDEX_FILE, index, "utf-8");
      console.log(`\n  [索引] README.md 已生成（${files.length} 个条目）`);
    } else {
      console.log(`\n  [索引] README.md 无变化`);
    }
  }

  // 检查 wiki/ 下是否有源目录已不存在的孤立文档
  if (!dryRun && fs.existsSync(TARGET_DIR)) {
    const synced = new Set(files);
    const orphaned = findMarkdownFiles(TARGET_DIR).filter(
      (rel) => rel !== "README.md" && !synced.has(rel)
    );
    if (orphaned.length > 0) {
      console.log(`\n⚠️  发现 ${orphaned.length} 个孤立文档（wiki/ 有但源目录没有）：`);
      orphaned.sort().forEach((o) => console.log(`  - ${o}`));
      console.log("  这些文件可能是之前删除的文档，如需清理请手动删除。");
    }
  }

  console.log(`\n完成！共处理 ${files.length} 个文档。`);
}

main();
