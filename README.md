# ITree

**Author: xalanq(iwtwiioi)**

**Email: xalanq@gmail.com(iwtwiioi@gmail.com)**

**Latest version: Alpha 1.5**

**License: LGPL V3.0**

**软件介绍及界面请看**: [我的博客](http://blog.xalanq.com/itree/)

## 下载二进制版本

[Windows 64位下载](https://github.com/xalanq/ITree/releases/download/Alpha1.5/ITree_Alpha_1.5_win_x86-64.zip)

移步到[发布页](https://github.com/xalanq/ITree/releases)查看更多历史版本。

## 安装

依赖语言:`Python 3`

依赖库:`PySide`, `mistune`

`PySide`的`Python36`版本可以在[这下载](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

使用前先将`./res/MathJax.zip`解压到该目录。

### 对于Linux的发行版

安装`swig`

然后终端里，进入软件目录的`filecode`文件夹，输入
```
swig -python -c++ itreefile.i
g++ -fPIC -Wall -Wextra -shared itreefile.cpp itreefile_wrap.cxx -o _itreefile.so -I/usr/include/python3.4m/
```
(将上边`/usr/include/python3.4m/`改为你自己的`python`库文件路径)

编译完以后将`itreefile.py`和`_itreefile.so`复制到软件主目录

然后`pip3 install pyside mistune`

运行`itree.py`

若Python3.4安装不起pyside，请重新编译Python3.4并加上`--enable-shared`参数编译，即
```
./configure --enable-shared
./make
sudo make install
sudo ln -s /usr/local/lib/libpython3.4m.so.1.0 /usr/lib64/libpython3.4m.so.1.0
```
然后(对于Fedora)
```
sudo dnf install pyside-tools python3-PyQt4-webkit python3-PyQt4-devel python-qt5
```
然后再
`pip3 install pyside mistune`

### 对于Windows

安装`Python 3.4`

运行`pip install mistune`和`pip install pyside --only-binary :all:`

安装`swig`

在命令行里，进入软件目录的`filecode`文件夹，输入
```
swig -python -c++ itreefile.i
```

用IDE建立新工程，编译动态库，将`itreefile.cpp`,`itreefile.h`,`itreefile_wrap.cxx`加入工程里并编译。

将编译好的dll文件改名为`_itreefile.pyd`，然后与`filecode`文件夹里的`itreefile.py`一起复制到软件主目录

## Q & A

### 1. 图片显示不正常

打开`imartdown.py`,搜索`assignTo`,替换`return`内容为注释内容

### 2. Windows下tex公式显示下标有问题，变成了上标

目前不知道什么回事...

不过将`Katex`换成`MathJax`后得到解决.

## 功能

* 主体用`markdown`作为编辑语言(由`mistune`作为引擎)
* 支持`Tex`(由`KaTex`或`MathJax`作为引擎,离线)
* 支持代码高亮(由`SyntaxHighlighter`作为引擎,离线)

# 更新历史

## Alpha 1.5 - 03/01/2018

* 将`Katex`换成`MathJax`

## Alpha 1.4 - 08/07/2017

* 添加捐赠
* 修复markdown公式问题
* 修复插入代码点击“打开”后ctrl+enter不能插入
* 修复文件管理器空白区域不能右键
* 修复Windows下不能进行第二次保存

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
