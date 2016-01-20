# ITree

**Author:iwtwiioi**

**Email:iwtwiioi@gmail.com**

**Latest version:Alpha 1.3**

**License:LGPL V3.0**

## Install

依赖语言:`Python 3`

依赖库:`PySide`, `mistune`

安装`pip install pyside mistune`

运行`itree.py`

## 功能

* 主体用`markdown`作为编辑语言(由`mistune`作为引擎)
* 支持`Tex`(由`MathJax`作为引擎,离线)
* 支持代码高亮(由`SyntaxHighlighter`作为引擎,离线)

# Version update list

## Alpha 1.4

* 修复markdown公式问题

## Alpha 1.3 - 01/19/2016

* 新增插入图片,图片浏览,图片下载等功能
* 新增插入文件,文件浏览,文件下载保存等功能
* 新增插入链接功能
* 新增设置等若干功能
* 新增了国际化
* 新增了节点若干功能
* 修复了文件保存打开等问题
* 修复了若干问题

Bugs:
* qt的QPlainText反复设置ReadOnly后导致输入法失效,因此妥协不使用ReadOnly
* 树状图不能拖放
* 预览界面的右键菜单问题
* 保存文件如果是大写则无后缀名添加在后面
* markdown不是很好支持math啊...

## Alpha 1.2 - 12/28/2015

* 新增代码高亮渲染(使用`syntaxhighlighter`),代码插入
* 去除了树状目录和编辑器的边框
* 美化字体.编辑界面默认使用`YaHei Consolas Hybrid`;显示界面默认使用`Helvetica`.
* 修复切换节点导致的undo/redo与modified

Bugs:

* qt的QPlainText反复设置ReadOnly后导致输入法失效,因此妥协不使用ReadOnly
* 显示界面右键菜单不太对
* 树状图拖放节点有问题
* 树状图的滚轮显示有问题
* 设置,插入图片,链接等均未实现.
* ~~代码高亮存在不显示完全(存在一点点滚动空间,导致滚轮出现)~~

## Alpha 1.1 - 12/16/2015

Bugs:

* 树状图拖放节点有问题
* 树状图的滚轮显示有问题
* 设置,插入功能等均未实现
