# 梓宸の流量消耗器

---

![GitHub](https://img.shields.io/github/license/zi-c/DataConsumer?style=flat-square)
![Lines of Code](https://tokei.rs/b1/github/zi-c/DataConsumer?category=code&label=Lines%20of%20Code&style=flat-square)

## 介绍
本工具旨在通过多线程下载指定文件测试当前宽带/流量的稳定性，以及途径相关设备的稳定性。
因为网页版的限制比较多，耗能也高，所以就使用Python3制作了这样一个工具。

## 功能
- 指定次数
- 指定下载链接
- 指定线程数量
- 随机 User-Agent

## 特点
- Windows/Linux 全平台兼容
- 采用流式下载，内存占用极低
- 代码小巧，功能强悍

---

设备运行内存占用公式：
最大内存占用 = 线程数量 x 分块大小
