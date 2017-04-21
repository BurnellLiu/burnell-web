burnell-web <br>
===========
burnell-web [www.burnelltek.com](http://www.burnelltek.com) 是一个个人博客网站系统，后端使用Python编写 <br>

# License <br>
**MIT** <br>

# 开发环境 <br>
Python3.5.2 <br>
Python依赖库：<br>
1. aiohttp，异步web框架库 <br>
2. jinja2， 前端模板引擎库 <br>
3. aiomysql，mysql异步驱动库 <br>
4. pillow，图片库用于生成验证码 <br>
5. pygments，代码高亮库 <br>

# 项目结构 <br>
>conf                  nginx和supervisor配置文件目录 <br>
>www                   web目录, 存放.py文件 <br>
>>config               web配置模块 <br>
>>static               存放静态文件 <br>
>>templates            存放模板文件 <br>

# 部署示例(阿里云ECS Ubuntu14.04) <br>
1. 安装SSH服务 <br>
sudo apt-get install openssh-server <br>

2. 安装Python3.5 <br>
sudo add-apt-repository ppa:fkrull/deadsnakes <br>
sudo apt-get update <br>
sudo apt-get install python3.5 <br>
如果无法识别add-apt-repository命令, 则需要进行如下操作: <br>
sudo apt-get install python-software-properties <br>
sudo apt-get install software-properties-common <br>

3. 取消原本的 Python 3.4 ，并将 Python3 链接到最新的 3.5 上：<br>
sudo mv /usr/bin/python3 /usr/bin/python3-old <br>
sudo ln -s /usr/bin/python3.5 /usr/bin/python3 <br>

4. 安装Python3包管理工具: python3-pip <br>
sudo apt-get install python3-pip <br>

5. 安装需要的Python库 <br>
sudo pip3 install jinja2 aiomysql aiohttp <br>
如果没有切换Python3链接的动作, 则pip3会把Python库安装在Python3.4上 <br>
安装pillow: <br>
sudo apt-get install python3.5-dev <br>
sudo apt-get install libjpeg8-dev zlib1g-dev libfreetype6-dev <br>
sudo pip3 install pillow <br>
安装pygments: <br>
sudo pip3 install pygments <br>

6. 切换回来链接文件：<br>
sudo rm /usr/bin/python3 <br>
sudo mv /usr/bin/python3-old /usr/bin/python3 <br>

7. 安装MySQL数据库服务 <br>
sudo apt-get install mysql-server <br>

8. 安装 Nginx：高性能Web服务器+负责反向代理: <br>
sudo apt-get install nginx <br>
  
9. 安装 Supervisor：监控服务进程的工具 <br>
sudo apt-get install supervisor <br>
启动 Supervisor: sudo supervisord <br>

10. 设置MySql可以远程链接 <br>
vim /etc/MySQL/my.cnf找到bind-address = 127.0.0.1 <br>
注释掉这行，如：#bind-address = 127.0.0.1 <br>
重启 MySQL：sudo /etc/init.d/mysql restart <br>
root登录mysql: mysql -u root -p <br>
授权远程链接: grant all privileges on *.* to root@"%" identified by "password" with grant option; <br>
刷新权限信息: flush privileges; <br>

11. 设置MySQL支持Emoji表情存储 <br>
找到/etc/mysql路径下的my.cnf文件，添加如下配置： <br>
[client] <br>
default-character-set=utf8mb4 <br>
[mysqld] <br>
character-set-client-handshake = FALSE <br>
character-set-server = utf8mb4 <br>
collation-server = utf8mb4\_unicode\_ci <br>
init_connect=’SET NAMES utf8mb4' <br>
[mysql] <br>
default-character-set=utf8mb4 <br>
root登录mysql: mysql -u root -p <br>
已经使用uft8创建的database可以做如下的字符集修改： <br>
ALTER DATABASE 数据库名 CHARACTER SET = utf8mb4 COLLATE = utf8mb4\_unicode\_ci; <br>
已经使用uft8创建的table可以做如下的字符集修改： <br>
ALTER TABLE 表名 CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4\_unicode\_ci; <br>
已经使用utf8创建的字段可以做如下的字符集修改： <br>
ALTER TABLE 表名 CHANGE 字段名 字段名 该字段原来的数据类型 CHARACTER SET utf8mb4 COLLATE utf8mb4\_unicode\_ci; <br>
重启 MySQL：sudo /etc/init.d/mysql restart <br>

12. 配置Supervisor <br>
编写一个Supervisor的配置文件burnellweb.conf，存放到/etc/supervisor/conf.d/目录下<br>
然后重启Supervisor后，就可以随时启动和停止Supervisor管理的服务了<br>
重启：sudo supervisorctl reload <br>
启动我们的服务：sudo supervisorctl start burnellweb <br>
查看状态：sudo supervisorctl status<br>
    ```
    [program:burnellweb]
    command     = python3.5 /srv/burnell_web/www/web_app.py
    directory   = /srv/burnell_web/www
    user        = www-data
    startsecs   = 3
    redirect_stderr         = true
    stdout_logfile_maxbytes = 50MB
    stdout_logfile_backups  = 10
    stdout_logfile          = /srv/burnell_web/log/app.log
    ```


13. 配置Nginx <br>
Supervisor只负责运行app.py，我们还需要配置Nginx，把配置文件burnellweb放到/etc/nginx/sites-available/目录下<br>
让Nginx重新加载配置文件：sudo /etc/init.d/nginx reload <br>
    ```
    server {
        listen      80;
        root       /srv/burnell_web/www;
        access_log /srv/burnell_web/log/access_log;
        error_log  /srv/burnell_web/log/error_log;
        # server_name burnelltek.com;
        client_max_body_size 1m;
        gzip            on;
        gzip_min_length 1024;
        gzip_buffers    4 8k;
        gzip_types      text/css application/x-javascript application/json;
        sendfile on;
        location /favicon.ico {
            root /srv/burnell_web/www/static/img;
        }
        location ~ ^\/static\/.*$ {
            root /srv/burnell_web/www;
        }
        location / {
            proxy_pass       http://127.0.0.1:9000;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```

# Release Note: <br>

## 2017/04/21 V1.1.5 Release <br>
1. 增加代码高亮功能 <br>
2. 评论功能改善 <br>
3. 评论管理页面增加被评博客链接 <br>
4. 调整手机上首页和博客列表页的布局 <br>
5. 后台博客显示修改 <br>
6. 后台管理按钮移到头像下拉列表中<br>
7. 管理博客页面分页改善 <br>
8. 管理评论页面分页改善 <br>
9. 管理用户页面分页改善 <br>
10. 使用UiKit的确认对话框取代原生确认对话框 <br>
11. 修改Mathjax使用$$作为行内公式标记 <br>

## 2017/02/13 V1.1.3 Release <br>
1. 增加微博登录功能 <br>
2. UI适配移动端 <br>
3. 将首页的作者信息替换为热门博客 <br>
4. 解决不能退出登陆的BUG <br>
5. 支持emoji表情的输入和显示 <br>
6. 所有博客标题设置为可以换行显示 <br>
7. 使用MathJax支持显示数学公式 <br>
8. 热门博客列表序号从0开始 <br>
9. 增加微博关注功能 <br>
10. 增加微博分享功能 <br>
11. 主页改版，增加微博展示 <br>
12. 博客增加版权信息 <br>
13. 上传图片，取消图片原始名称 <br>
14. 配置档中增加配置域名信息 <br>
15. 微博登陆后获取微博用户的高清头像，替换原来的50*50头像 <br>
16. 管理用户界面显示用户头像（代替Email） <br>
17. 配置档增加网站名称、ICP备案号、微博APP_KEY和微博UID的配置项 <br>

## 2016/12/01 V1.1.2 Release <br>
1. 增加博客分类 <br>
2. 增加作者简介 <br>
3. 重新设计首页 <br>
4. 增加热门博客信息 <br>
5. 增加备案信息 <br>
6. 完成博客分页 <br>

## 2016/11/27 V1.1.1 Release <br>
1. 限制每10秒只能发送一条评论 <br>
2. 注册账号页面需要输入验证码 <br>







