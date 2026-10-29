/**
 * Opencode Skills → Qoder Skills 同步脚本
 *
 * 功能：读取 .opencode/skills/ 下所有 SKILL.md 文件，
 *      去掉 YAML frontmatter，写入 .qoder/skills/ 对应的 .skill 文件。
 *
 * 用法：node sync-skills.js [--dry-run]
 *
 * 参数：
 *   --dry-run  只显示将要执行的操作，不实际写入文件
 */

const fs = require("fs");
const path = require("path");

// 项目根目录（脚本所在目录的上一级）
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.dirname(SCRIPT_DIR);

const OPENCODE_SKILLS_DIR = path.join(PROJECT_ROOT, ".opencode", "skills");
const QODER_SKILLS_DIR = path.join(PROJECT_ROOT, ".qoder", "skills");

/**
 * 去掉 SKILL.md 文件顶部的 YAML frontmatter（--- ... ---）
 */
function stripYamlFrontmatter(content) {
  return content.replace(/^---\s*\n[\s\S]*?\n---\s*\n/, "");
}

/**
 * 扫描 .opencode/skills/ 目录，找到所有 SKILL.md 文件
 */
function findOpencodeSkills(baseDir) {
  const skills = [];
  const layers = fs.readdirSync(baseDir);

  for (const layer of layers) {
    const layerPath = path.join(baseDir, layer);
    if (!fs.statSync(layerPath).isDirectory()) continue;

    const names = fs.readdirSync(layerPath);
    for (const name of names) {
      const namePath = path.join(layerPath, name);
      if (!fs.statSync(namePath).isDirectory()) continue;

      const skillMd = path.join(namePath, "SKILL.md");
      if (fs.existsSync(skillMd)) {
        skills.push({ layer, name, source: skillMd });
      }
    }
  }

  return skills;
}

/**
 * 同步单个 skill 文件
 */
function syncSkill(skillInfo, dryRun) {
  const { layer, name, source } = skillInfo;

  // 读取源文件
  const content = fs.readFileSync(source, "utf-8");

  // 去掉 YAML frontmatter
  const converted = stripYamlFrontmatter(content);

  // 目标路径
  const targetDir = path.join(QODER_SKILLS_DIR, layer);
  const targetFile = path.join(targetDir, `${name}.skill`);

  // 检查是否有变化
  let changed = true;
  let status;
  if (fs.existsSync(targetFile)) {
    const existing = fs.readFileSync(targetFile, "utf-8");
    if (existing === converted) {
      changed = false;
      status = "无变化";
    } else {
      status = "更新";
    }
  } else {
    status = "新建";
  }

  if (dryRun) {
    console.log(`  [${status}] ${layer}/${name}.skill`);
    return;
  }

  if (!changed) {
    console.log(`  [无变化] ${layer}/${name}.skill`);
    return;
  }

  // 确保目录存在
  fs.mkdirSync(targetDir, { recursive: true });

  // 写入目标文件
  fs.writeFileSync(targetFile, converted, "utf-8");
  console.log(`  [${status}] ${layer}/${name}.skill`);
}

/**
 * 主函数
 */
function main() {
  const dryRun = process.argv.includes("--dry-run");

  console.log("=".repeat(50));
  console.log("Opencode Skills → Qoder Skills 同步");
  console.log("=".repeat(50));

  if (!fs.existsSync(OPENCODE_SKILLS_DIR)) {
    console.log(`错误：找不到源目录 ${OPENCODE_SKILLS_DIR}`);
    process.exit(1);
  }

  if (dryRun) {
    console.log("（dry-run 模式，不实际写入文件）");
  }

  console.log(`\n源目录：${OPENCODE_SKILLS_DIR}`);
  console.log(`目标目录：${QODER_SKILLS_DIR}`);
  console.log();

  // 扫描源文件
  const skills = findOpencodeSkills(OPENCODE_SKILLS_DIR);
  console.log(`找到 ${skills.length} 个 skill 文件：\n`);

  // 排序后同步
  skills
    .sort((a, b) => a.layer.localeCompare(b.layer) || a.name.localeCompare(b.name))
    .forEach((skill) => syncSkill(skill, dryRun));

  console.log(`\n完成！共处理 ${skills.length} 个文件。`);

  // 检查 Qoder 端是否有孤立的 .skill 文件
  if (!dryRun) {
    const qoderSkills = new Set();
    const opencodeSkills = new Set();

    for (const layer of fs.readdirSync(QODER_SKILLS_DIR)) {
      const layerPath = path.join(QODER_SKILLS_DIR, layer);
      if (!fs.statSync(layerPath).isDirectory()) continue;
      for (const f of fs.readdirSync(layerPath)) {
        if (f.endsWith(".skill")) {
          qoderSkills.add(`${layer}/${f.slice(0, -6)}`);
        }
      }
    }

    for (const skill of skills) {
      opencodeSkills.add(`${skill.layer}/${skill.name}`);
    }

    const orphaned = [...qoderSkills].filter((s) => !opencodeSkills.has(s));
    if (orphaned.length > 0) {
      console.log(`\n⚠️  发现 ${orphaned.length} 个孤立文件（Qoder 有但 Opencode 没有）：`);
      orphaned.sort().forEach((o) => console.log(`  - ${o}.skill`));
      console.log("  这些文件可能是之前删除的 skill，如需清理请手动删除。");
    }
  }
}

main();
