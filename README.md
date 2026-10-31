# Biomolecular 3D

**把 RCSB PDB 的真实分子坐标，变成可旋转、可近看、可讲解的三维科普模型。**

A Codex skill for building interactive biomolecular models from RCSB PDB coordinates: proteins, DNA, RNA, and molecular complexes.

适合做面向中小学生的互动科普页，也适合给已有 Three.js 项目添加分子模型。Skill 提供结构选择、坐标处理、几何生成、教学交互和验证流程，以及可复用的数据脚本；它不是一套已经打包好的网页应用。下图是使用这套流程制作的 WonderLab X 实例，示例页面源码不包含在本仓库中。

## 实例

<table>
  <tr>
    <th>ATP 合酶：纳米旋转机器</th>
    <th>DNA：双螺旋里的生命信息</th>
  </tr>
  <tr>
    <td valign="top"><img src="docs/images/atp-synthase.png" width="440" alt="ATP 合酶互动科普模型，展示固定支架、中央轴、转子环和 ATP 合成部位"></td>
    <td valign="top"><img src="docs/images/dna-double-helix.png" width="440" alt="DNA 双螺旋原子视图，可旋转缩放并观察碱基和链方向"></td>
  </tr>
</table>

### ATP 合酶 · PDB 6CP6

从酵母 ATP 合酶的真实结构出发，按固定支架、中央轴、转子环和 ATP 合成部位分组，设计整体观察、转子近看、催化过程和单步控制。

- **结构数据**：[RCSB 6CP6](https://www.rcsb.org/structure/6CP6)，酵母线粒体 ATP 合酶，冷冻电镜，分辨率 3.60 Å。
- **原始研究**：Srivastava et al., *High-resolution cryo-EM analysis of the yeast ATP synthase in a lipid membrane*, Science (2018), [DOI](https://doi.org/10.1126/science.aas9699)。
- **表示方式**：基于 Cα 坐标的轻量包络，适合看整体部件；不是全原子表面或电镜密度图。
- **教学取舍**：脂质膜、颜色、粒子、放慢的旋转和催化开合为教学示意。该条目只提供静态构象，不能据此声称恢复了真实运动轨迹；c₁₀ 转子环数量也不能推广到所有物种。

### DNA 双螺旋 · PDB 1BNA

从真实 DNA 坐标制作双螺旋、单对碱基和原子三种观察方式，突出 A–T / C–G 配对及两条链的方向。

- **结构数据**：[RCSB 1BNA](https://www.rcsb.org/structure/1BNA)，12 对碱基的合成 B-DNA 片段，X 射线衍射，分辨率 1.90 Å。
- **原始研究**：Drew et al., *Structure of a B-DNA dodecamer: conformation and dynamics*, PNAS (1981), [DOI](https://doi.org/10.1073/pnas.78.4.2179)。
- **表示方式**：原子视图保留元素身份，并依据化学拓扑处理共价键；不把核酸套进蛋白 Cα 包络算法。
- **教学取舍**：这是一个短 DNA 片段；颜色和球棍大小服务于阅读，不是电子显微镜照片，也不是完整染色体。

两张图由作者提供，来自 WonderLab X 自制页面，展示可达到的教学呈现方式。

## 安装 Skill

### 方法一：让 Codex 安装

在 Codex 中输入：

```text
用 $skill-installer 安装这个 GitHub 仓库根目录的 skill：
https://github.com/rockeymen/biomacromolecule-3d
安装名称使用 biomacromolecule-3d。
```

支持安装器脚本的 Codex 环境也可运行：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo rockeymen/biomacromolecule-3d \
  --path . \
  --name biomacromolecule-3d
```

安装器脚本随 Codex 环境提供，不属于本仓库；没有该脚本时使用下面的 Git 方法。安装器遇到同名目录会停止，不会覆盖已有 skill。

### 方法二：Git 安装

需要本机已安装 Git。在终端执行：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/rockeymen/biomacromolecule-3d.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/biomacromolecule-3d"
```

安装后的目录应为：

```text
~/.codex/skills/biomacromolecule-3d/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
└── references/
```

设置了 `CODEX_HOME` 时，以该目录下的 `skills/` 为准。安装后在下一轮对话调用；若列表尚未刷新，重新打开 Codex 后再试。

**更新 Git 安装：**

```bash
git -C "${CODEX_HOME:-$HOME/.codex}/skills/biomacromolecule-3d" pull --ff-only
```

若之前是手动复制或安装器安装、目录里没有 `.git`，先备份并移走原目录，再重新安装。已有修改先保留，避免直接覆盖。

## 调用示例

安装后在自己的网页项目中告诉 Codex：

```text
用 $biomacromolecule-3d，把 RCSB 的 1BNA 做成可交互的 DNA 三维科普网页。
面向小学高年级到初中，支持拖动旋转、缩放、观察一对碱基和原子视图，
标注真实数据来源与教学简化，先给本地预览。
```

```text
用 $biomacromolecule-3d，把 RCSB 的 6CP6 做成 ATP 合酶科普模型。
区分固定支架、中央转轴、c 环和催化头，加入暂停和 120° 单步，
明确说明运动是教学示意。
```

也可以直接给 RCSB 条目链接，或先让 Codex 挑选适合某个教学主题的结构。部署仍按你的明确请求执行。

## 数据从哪里来？

[RCSB PDB](https://www.rcsb.org/pages/about-us/index) 是全球 Protein Data Bank（PDB）档案的成员机构与访问门户。结构由研究者提交，经档案标准化与验证；本流程下载的是可追溯的坐标文件，优先使用 **PDBx/mmCIF**，不是根据图片猜测分子形状。

每次使用都应保留 **PDB ID、所选装配体、下载 URL、获取时间、文件 SHA256 和原始论文**。RCSB 同时提供实验结构与计算结构模型的访问；后者必须明确标记为预测，不能与实测结构混称。参见 [RCSB 文件下载服务](https://www.rcsb.org/docs/programmatic-access/file-download-services)。

### 主要有哪些大分子？

按分子成分，核心类别是蛋白质、DNA 和 RNA；按组成层级，还可制作多种复合物。下表用于教学选题，类别可能交叉，不是互斥的官方统计分类。[RCSB 官方介绍](https://www.rcsb.org/pages/about-us/index)

| 类别 | 可以找什么 | 适合做的互动科普 |
| --- | --- | --- |
| **蛋白质** | 酶、抗体、受体、离子通道、马达蛋白、结构蛋白 | 酶与底物如何结合、抗体如何识别目标、分子机器如何工作 |
| **DNA** | 双螺旋、短片段及不同构象 | 碱基互补配对、双链方向、大小沟与信息编码 |
| **RNA** | tRNA、rRNA、核酶等 | RNA 如何折叠、tRNA 如何携带氨基酸、RNA 的结构与功能 |
| **多亚基与混合复合物** | 蛋白质复合物、蛋白–DNA、蛋白–RNA、核糖体、核小体、病毒衣壳等 | 分子之间如何协作、DNA 如何缠绕、蛋白质如何被制造、衣壳如何装配 |

条目中也常有 **糖链、药物、ATP 等小分子、色素和金属离子**，有助于解释糖基化、能量转换与结合位点。其中药物、ATP、金属离子不属于生物大分子本身；一个条目也不一定包含完整的细胞结构或整个病毒。适合叙事的官方教学资料见 [PDB-101](https://pdb101.rcsb.org/)。

## 随附脚本与依赖

安装 skill 本身只需要文件；执行坐标提取时才需要 Python 环境，生成蛋白包络时才需要 Node.js 与目标项目的 Three.js。

| 脚本 | 功能 | 依赖 |
| --- | --- | --- |
| `scripts/fetch_structure.py` | 下载条目或已展开装配体的 mmCIF，保存来源与 SHA256 | Python 3 标准库、网络 |
| `scripts/extract_coordinates.py` | 提取全重原子、蛋白 Cα 或核酸骨架，保留身份并统一转换到 nm | Python 3、gemmi、numpy |
| `scripts/build_ca_surface.mjs` | 按链生成轻量蛋白 Cα 包络与元数据 | Node.js、目标项目已有的 Three.js |

建议在独立虚拟环境安装 Python 依赖：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/biomacromolecule-3d"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python scripts/fetch_structure.py 1BNA --out temp/1bna
.venv/bin/python scripts/extract_coordinates.py \
  --input temp/1bna/1BNA.cif \
  --representation atoms \
  --out temp/1bna/atoms.json
```

以上生成可用于建模的坐标 JSON；页面、化学键拓扑和教学交互由 Codex 根据目标项目继续实现。脚本遇到已有输出会停止，重复运行请换一个输出目录或文件名。

`ca` 仅用于蛋白质；`nucleic` 只输出 P/C4′ 骨架采样，不包含完整碱基或配对。蛋白包络的构建命令与解码格式见 [SKILL.md](SKILL.md) 和 [数据与几何契约](references/data-and-geometry.md)。

## 科学表达与流程边界

- 核对实验/预测、物种、缺失部分、构象、配体和生物装配体；不把晶体接触自动当成真实复合物。
- 全部链使用同一坐标变换；Å → nm 乘以 0.1，不逐链缩放或移动来“拼好看”。
- 原子结构、Cα 包络和实验密度是不同表示；静态结构不能单独证明运动轨迹。
- 模型几何、标签和读数保持一致；网页交付时实际检查旋转、缩放、选择、窄屏与动态效果设置。

详细流程：[技能入口](SKILL.md) · [数据与几何](references/data-and-geometry.md) · [ATP 合酶实例](references/atp-synthase-example.md) · [验证与项目接入](references/verification-and-integration.md)。

## 许可与致谢

本仓库原创 skill、脚本、说明及作者提供的示例截图采用 [MIT License](LICENSE)。

**PDB 档案坐标数据采用 CC0 1.0**；建议引用具体 PDB ID 与结构作者论文。本仓库的 MIT 许可不改变第三方数据、软件或插图的许可，RCSB 网页和 PDB-101 插画也不能自动按坐标数据的 CC0 处理。详情见 [RCSB 引用与使用政策](https://www.rcsb.org/pages/policies)。

感谢结构研究者、wwPDB / RCSB PDB，以及 Gemmi、NumPy、Three.js 等开源项目。此项目由社区独立制作，与 RCSB PDB 无隶属关系。
