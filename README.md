# 深圳信息职业技术学院自动抢体育俱乐部脚本 留给师弟师妹用吧！
## 2022.06.11 版本V1.0
## 使用说明（Linux）：
### 关于依赖
请先确保您有python3.6及以上环境<br/>
在云服务器上安装依赖 
```
pip3 install -r requirements.txt
```
腾讯云的云函数已经拥有了自己的终端，那么我们不再需要创建层了，请将今日校园文件夹里的代码打包成zip并上传到腾讯云，最后到requirements.txt目录（一般情况应该也就是上传后的src目录里）执行以下命令

（腾讯云函数新版本编辑器，下方有个终端，打开它，并且执行cd ./src即可进入到src目录）
```
pip install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple
```
当然，盲猜你们都是python3，那么请使用pip3代替pip

也就是
```
pip3 install -r requirements.txt -t ./ -i https://mirrors.aliyun.com/pypi/simple
```
# 禁止售卖脚本赚钱，脚本仅供学习使用，责任与本人无关！
# 本脚本兼容多用户，建议使用多用户模式
