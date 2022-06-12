# 深圳信息职业技术学院抢体育俱乐部脚本
## 2022.06.11 版本V1.0
## 使用说明（Linux）：
### 关于依赖


请先确保您有python3.6及以上环境<br/>
```
yum install python3
```

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
### 关于推送
本脚本采用邮箱推送（说人话就是抢到了会发邮件通知你）<br/>
由于作者编程水平有限，请填写好config.yml中的每一项内容，不然就会出奇奇怪怪的报错
smtp密码的获取请参考下文
```
https://boke112.com/post/3253.html
```

### 关于腾讯云函数
请在腾讯云函数上直接上传本压缩包文件<br/>
请在
```
 https://console.cloud.tencent.com/cam/capi 
```
获取SecretId 和 SecretKey 并填写至config文件中

请将腾讯云函数名填写至index.py文件167行"FunctionName"：后

详情请参考腾讯云函数调用API
```
https://console.cloud.tencent.com/api/explorer?Product=scf&Version=2018-04-16&Action=Invoke&SignVersion=
```

### 使用说明
作者推荐使用一台云服务器（Linux）+ 腾讯云函数搭配使用 防止IP被ban导致漏抢俱乐部

也可只在服务器上部署，只需执行对indexSCF文件进行少量的修改便可直接使用。
#### 单服务器部署 
请先参考关于依赖的服务器部署
```
python3 indexone.py
```

#### 关于config中的jlb_url 需要手动获取。
1. 请先打开 https://ehall.sziit.edu.cn/new/index.html 进行登录
2. 登录后请点击 体育俱乐部 
3. ![1655012815283](https://user-images.githubusercontent.com/73678111/173217554-83227ea0-cb93-4977-bf3b-5bd537901657.png)
4. 请复制上图中的URL填写至config文件中



# 禁止售卖脚本赚钱，脚本仅供学习使用，所带来的的责任与本人无关！
# 本脚本兼容多用户，建议使用多用户模式
