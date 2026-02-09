> [!TIP]  
> ***This project is one of the THOUGHT OF THE DAY projects.***  
> ***该项目是“每日灵感记录”系列项目之一。***  
> *The development of these project may not be active.*  
> *这些项目的开发可能不会活跃。*  

## IgnisCAD

[![PyPI version](https://img.shields.io/pypi/v/igniscad.svg)](https://pypi.org/project/igniscad/)
[![Python versions](https://img.shields.io/pypi/pyversions/igniscad.svg)](https://pypi.org/project/igniscad/)
[![License](https://img.shields.io/pypi/l/igniscad.svg)](https://github.com/CreeperIsASpy/igniscad/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/igniscad)](https://pepy.tech/project/igniscad)

使用 Python 封装 build123d 进行 CAD 开发，让 AI 智能体可以使用纯文本建模。  
*A wrapper for the build123d library, designed for AI agents.*  


### 使用 Usage
使用 PyPI 下载该包：   
*Download the package via PyPI:*
```shell
python -m pip install igniscad
```
由于项目正在快速更新，因此不建议您使用镜像源。  
*Using mirror sources is not recommended due to the early developing of the project.*

### API

整个项目围绕 *Entity* 类构造，您可以使用 *Model* 类来创造一个模型，并在其中添加和改造 *Entity*。  
*The whole project is based on the class ***Entity***, you can create a model via calling the class ***Model***, 
and try adding or modifying some ***Entity*** inside it.*

每个 *Entity* 都是一个 *build123d* 类库的封装，有些是类，有些则是工厂函数。   
*Every ***Entity*** is a wrapper for ***build123d*** classes, which can be primitive functions or subclasses.*

每个 *Entity* 在定义时都有一个 *name* 属性，您可以通过 *name* 属性来在模型中快速查找一个特定的 *Entity*。  
*Each ***Entity*** has a ***name*** property while defining, 
you can use the ***name*** property to find a specified ***Entity*** in the model immediately.  
这样可以保证上下文的统一性，也有助于进行原子性修改：  
*This ensures the consistency of context and facilitates atomic modifications:*  
```python
from igniscad import *
with Model("Example") as model:
    model << Cylinder(5, 38, "pole")
    model.find("pole") # Returns the original Cylinder.
```

### 图表 Charts
![Alt](https://repobeats.axiom.co/api/embed/1deed7c62764e4f62cfd7b1dafd85555866e14eb.svg "Repobeats analytics image")

