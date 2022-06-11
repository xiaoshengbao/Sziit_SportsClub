import datetime
import re
import smtplib
import time
import urllib.parse
import requests
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from actions.Utils import Utils
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models

# 通过信息门户，登录至校园网
def login_session_url(username, password, login_url):
    html = session.get(login_url, verify=False).text
    soup = BeautifulSoup(html, 'lxml')
    if len(soup.select('#casLoginForm')) > 0:
        type = 0
    elif len(soup.select('#pwdFromId')) > 0:
        soup = BeautifulSoup(str(soup.select('#pwdFromId')[0]), 'lxml')
        type = 1
    elif len(soup.select('#fm1')) > 0:
        soup = BeautifulSoup(str(soup.select('#fm1')[0]), 'lxml')
        type = 2
    else:
        raise Exception('出错啦！网页中没有找到LoginForm')
    # 填充数据
    params = {}
    form = soup.select('input')
    for item in form:
        if None != item.get('name') and len(item.get('name')) > 0:
            if item.get('name') != 'rememberMe':
                if None == item.get('value'):
                    params[item.get('name')] = ''
                else:
                    params[item.get('name')] = item.get('value')
    params['username'] = username
    # 获取密钥
    if type == 2:
        pattern = 'RSAKeyPair\((.*?)\);'
        publicKey = re.findall(pattern, html)
        publicKey = publicKey[0].replace('"', "").split(',')
        params['password'] = Utils.encryptRSA(password, publicKey[2],
                                              publicKey[0])
        params['captcha'] = ''
    else:
        if type == 0:
            salt = soup.select("#pwdDefaultEncryptSalt")
        else:
            salt = soup.select("#pwdEncryptSalt")
        if len(salt) != 0:
            salt = salt[0].get('value')
        else:
            pattern = '\"(\w{16})\"'
            salt = re.findall(pattern, html)
            if len(salt) == 1:
                salt = salt[0]
            else:
                salt = False
        if not salt:
            params['password'] = password
        else:
            params['password'] = Utils.encryptAES(
                Utils.randString(64) + password, salt)
    parser = urllib.parse.urlencode(params)
    return parser


# 跳转到俱乐部app，开始抢俱乐部
def get_login_url_cookie(parser, login_url, headers, jlb_url, username, receviers):
    # 拿到ck
    data = session.post(login_url,
                        data=parser[0:19] + parser[33:],
                        headers=headers
                        , allow_redirects=False)
    jump_url = data.headers['Location']
    session.get(jump_url, verify=False)

    # 通过ck直接跳转访问俱乐部
    session.get(jlb_url, verify=False)

    # 通过post请求拿到活动列表
    hd_url = 'https://ehall.sziit.edu.cn/qljfwapp/sys/szxxtyjlbapp/modules/hdyy/getHdyyData.do'
    hd = session.post(hd_url).json()
    # 抢到了返回Flase，没有抢到返回True
    jlb = True
    ret = True
    # 如果有活动则开始抢
    if hd['datas']['getHdyyData']['totalSize'] != 0 or hd['datas']['getHdyyData']['totalSize'] != None:
        for i in hd['datas']['getHdyyData']['rows']:
            par = {
                'WID': i['WID']
            }
            makeapphd = session.post('https://ehall.sziit.edu.cn/qljfwapp/sys/szxxtyjlbapp/hdyy/makeAppointmentHd.do',
                                     params=par).json()
            # code返回值如果不等于-1则可能已经预约成功
            if makeapphd['code'] != '-1':
                # 可能已经抢到了
                try:
                    print((datetime.datetime.now()).strftime("%Y-%m-%d, %H:%M:%S"), '活动标题:{}'.format(i['HDMC']),
                          makeapphd['msg'])
                except KeyError:
                    title = i['HDMC']
                    print((datetime.datetime.now()).strftime("%Y-%m-%d, %H:%M:%S"),
                          '活动标题:{}已成功预约,正在发送通知邮件'.format(i['HDMC']))
                    e_mail(receviers, title, username)
                    jlb = False
            else:
                print((datetime.datetime.now()).strftime("%Y-%m-%d, %H:%M:%S"), '活动标题:{}'.format(i['HDMC']),
                      makeapphd['msg'])
                jlb = True
            # 只要有一次抢到了，就返回抢到了，防止变量被二次覆盖
            if jlb == False:
                ret = jlb
    else:
        print('现在还没有体育俱乐部')
    return ret


def e_mail(receviers, title, username):
    config = Utils.getYmlConfig()
    mail_host = config['notifyOption']['smtpOption']['server']
    mail_user = config['notifyOption']['smtpOption']['userName']  # 用户名
    mail_pass = config['notifyOption']['smtpOption']['passWord']  # smtp登录口令

    sender = mail_user  # 发件人

    # message = MIMEText("这是正文内容随便","plain","utf-8")#构造正文内容随便
    message = MIMEMultipart()
    message["From"] = sender  # 发件人
    message['To'] = ';'.join(receviers)
    message["Subject"] = "已经抢到俱乐部啦！"  # 邮件的标题
    message.attach(MIMEText(
        '{} 用户{}俱乐部活动{}已被抢到'.format((datetime.datetime.now()).strftime("%Y-%m-%d, %H:%M:%S"), username,
                                    title)))  # 邮件正文内容

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 587)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receviers, message.as_string())  # 发送邮件
        print('发送成功')
    except:
        print('发送失败')

# 把config文件上传到腾讯云函数的系统变量中
def auto_jlb_all(config):
    config = Utils.getYmlConfig()
    SecretId = config['notifyOption']['SCFOption']['SecretId']
    SecretKey = config['notifyOption']['SCFOption']['SecretKey']
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "scf.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = scf_client.ScfClient(cred, "ap-guangzhou", clientProfile)

        req = models.UpdateFunctionConfigurationRequest()
        params = {
            "FunctionName": "",   #腾讯云函数名称，需要手动填写
            "Environment": {
                "Variables": [
                    {
                        "Key": "Config",
                        "Value": str(config)
                    }
                ]
            }
        }
        req.from_json_string(json.dumps(params))

        resp = client.UpdateFunctionConfiguration(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)
# 使用通讯云把所有人跑一遍
def auto_jlb_all_run():
    config = Utils.getYmlConfig()
    SecretId = config['notifyOption']['SCFOption']['SecretId']
    SecretKey = config['notifyOption']['SCFOption']['SecretKey']
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "scf.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = scf_client.ScfClient(cred, "ap-guangzhou", clientProfile)

        req = models.InvokeRequest()
        params = {
            "FunctionName": ""  #腾讯云函数的名称
        }
        req.from_json_string(json.dumps(params))

        resp = client.Invoke(req)
        a = json.loads(resp.to_json_string())
        if a['Result']['RetMsg'] == 'true':
            return True
        elif a['Result']['RetMsg'] == 'false':
            return False
    except TencentCloudSDKException as err:
        print(err)



def auto_jlb():
    login_url = 'https://auth.sziit.edu.cn/authserver/login?service=https%3A%2F%2Fehall.sziit.edu.cn%3A443%2Flogin%3Fservice%3Dhttps%3A%2F%2Fehall.sziit.edu.cn%2Fnew%2Findex.html'
    global session
    # 数据集
    config = Utils.getYmlConfig()
    auto_jlb_all(config)
    print('正在同步Config文件')
    for users in config['users']:
        session = requests.session()
        username = users['user']['username']
        password = users['user']['password']
        receviers = users['user']['e_mail']
        jlb_url = users['user']['jlb_url']
        print('当前用户{}'.format(username))
        headers = {
            'User-Agent':
                'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.34',
            'Content-Type': 'application/x-www-form-urlencoded'}
        parser = login_session_url(username, password, login_url)
        a = get_login_url_cookie(parser, login_url, headers, jlb_url, username, receviers)
        if a:
            print('当前所有活动都已经满人啦，等待5分钟后执行下一用户')
            # 保证30分钟内跑完整个代码
            time.sleep(180)
        else:
            b = auto_jlb_all_run()
            if b == False:
                break


def main():
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '08:00', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '20:00', '%Y-%m-%d%H:%M')

    # 当前时间
    n_time = datetime.datetime.now()
    # 判断当前时间是否在时间范围内
    if n_time > d_time and n_time < d_time1:
        auto_jlb()
    else:
        print('当前不在8点到20点之间')


if __name__ == '__main__':
    a = auto_jlb_all_run()
    print(a)
    print('30分钟后继续预约俱乐部')

