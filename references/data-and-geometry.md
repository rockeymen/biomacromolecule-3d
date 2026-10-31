# 数据与几何契约

## 下载和解析

- [RCSB 文件服务](https://www.rcsb.org/docs/programmatic-access/file-download-services)：条目 mmCIF 与 `ID-assemblyN.cif` 是不同选择。下载条目不会替你展开 biological assembly。展开后的坐标文件不要再次应用操作矩阵。
- mmCIF 推荐使用真实解析器（随附提取器依赖 gemmi、numpy）；不要按空格拆行解析带引号、分号多行及 loop 数据。
- `label_asym_id` / `auth_asym_id`、实体 ID、`label_seq_id` / `auth_seq_id` 和插入码分别保留。一个实体可有多条链；装配拷贝可能共享作者链名。组件名称按条目实体注释/论文核对，不按字母猜测。
- `_entity_poly.type` 用于区分多肽、核酸。`CA` 必须是多肽中的碳原子，不是钙离子；修改残基可能在 HETATM 中，不能一刀切丢掉所有 HETATM。
- 配体、核苷酸、金属、糖和水按教学目的保留/省略。任何影响机制解释的省略写入说明。Ca/Mg 等离子不能沿用蛋白或共价键规则。
- 默认选择一个明确模型，保留原编号。选择 alternate 时按残基统一选择一套替代构象，不逐原子随意拼接；共同 blank 原子可保留。缺失的残基、侧链和低占有率不是“自动补洞”的理由。

随附脚本的 altloc 规则是“残基内总占有率最高，字母序打破平局”，不是为所有实验数据保证最佳选择；关键结合位点请手动核对。`nucleic` 模式导出 P 与 C4′ 坐标，只是骨架取样；切勿把这些点当成完整 RNA/DNA 的表面或碱基配对。

## 坐标与资产

Å → nm 乘 0.1。只对整个体系做同一平移/旋转/统一缩放，保存逆变换所需原点和正交基。不要逐链居中后丢失相互位置。

提取器输出 `rcsb-coordinates-v1`：

- `sourceToWorld.originNm` 是原始 Å 坐标乘 0.1 后的平移原点；`basisRows` 左乘平移后的点。
- `chains[].id` 是 label 链，`authId` 是作者链，`entityId` 是实体；`points` 为 nm 坐标，`atoms` 同序保留原子/残基身份。不能把 P/C4′ 两个点计成两个核苷酸。
- `inputSha256` 绑定当前坐标文件；同目录下载 manifest 另外保存 URL、装配体和时间。

可选包络构建器仅接受蛋白 `ca` 数据。它用 Three.js MarchingCubes，按链创建连续的可视包络，再合并顶点、单位化法线。固定种子并不能把随机球堆变成真实结构；基础形状必须来自源坐标。Cα 包络的凹陷不能当成原子通道证据。

## 包络解码

`rcsb-ca-envelope-v1` 采用分链局部量化，避免大分子平移后溢出 int16。与 ATP 首版资产的绝对坐标编码不同；不要复用旧解码器。

```js
const packed = new Int16Array(buffer, chain.vertexOffset, chain.vertices * 6);
for (let i = 0; i < chain.vertices; i++) {
  for (let j = 0; j < 3; j++) {
    positions[i * 3 + j] = chain.centerNm[j] + packed[i * 6 + j] * chain.positionUnitNm;
    normals[i * 3 + j] = packed[i * 6 + 3 + j] / metadata.normalDivisor;
  }
}
const indices = chain.indexBytes === 4
  ? new Uint32Array(buffer, chain.indexOffset, chain.indexCount)
  : new Uint16Array(buffer, chain.indexOffset, chain.indexCount);
```

编码为 little-endian；上例适用于常见 little-endian 浏览器平台，其他字节序用 DataView 读取 LE。将数组装入 BufferGeometry；保留链/功能部件身份，正确计算包围球，按实际需要处理是否封闭、背面和阴影。构建器对每条链 4-byte 对齐，超出 uint16 顶点数时改用 uint32 索引；不要静默截断。

## 表面与细节取舍

- 晶体学/冷冻电镜坐标、预测坐标、原始密度图、原子表面是不同数据与表示。
- Cα 包络适合轻量整体轮廓；丝带需要可靠主链连接/二级结构，跨缺失残基时断开。球棍与结合口袋需保留原子身份、配体及拓扑信息。
- 糖链连接、二硫键和配体键不能凭相近距离猜成普通肽键。密度图可另用成熟工具读取，不从 Cα 生成后称为电镜密度。
- 网格太粗而包络变形/消失时，提高分辨率或换表示；不要无限放大包络半径掩盖问题。量化精度和参数保留在元数据中。
