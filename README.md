burnell-web
===========
burnell-web [www.burnelltek.com](www.burnelltek.com) 是一个个人博客网站系统，后端使用Python编写。

# 开发环境
Python3.5.2<br>
Python依赖库：<br>
1. aiohttp，异步web框架库<br>
2. jinja2， 前端模板引擎库<br>
3. aiomysql，mysql异步驱动库<br>

# 项目结构
>backup                备份目录<br>
>conf                  配置文件目录<br>
>dist                  打包目录<br>
>www                   web目录, 存放.py文件<br>
>>static               存放静态文件<br>
>>templates            存放模板文件<br>

# 部署示例(阿里云ECS Ubuntu14.04)
1. 安装SSH服务<br>
sudo apt-get install openssh-server<br>

2. 安装Python3.5<br>
sudo add-apt-repository ppa:fkrull/deadsnakes<br>
sudo apt-get update<br>
sudo apt-get install python3.5<br>
如果无法识别add-apt-repository命令, 则需要进行如下操作:<br>
sudo apt-get install python-software-properties<br>
sudo apt-get install software-properties-common<br>

3. 取消原本的 Python 3.4 ，并将 Python3 链接到最新的 3.5 上：<br>
sudo mv /usr/bin/python3 /usr/bin/python3-old<br>
sudo ln -s /usr/bin/python3.5 /usr/bin/python3<br>

4. 安装Python3包管理工具: python3-pip<br>
sudo apt-get install python3-pip<br>

5. 安装需要的Python库<br>
sudo pip3 install jinja2 aiomysql aiohttp<br>
如果没有切换Python3链接的动作, 则pip3会把Python库安装在Python3.4上<br>

6. 切换回来链接文件：<br>
sudo rm /usr/bin/python3<br>
sudo mv /usr/bin/python3-old /usr/bin/python3<br>

7. 安装MySQL数据库服务<br>
sudo apt-get install mysql-server<br>

8. 安装 Nginx：高性能Web服务器+负责反向代理: <br>
sudo apt-get install nginx<br>
  
9. 安装 Supervisor：监控服务进程的工具<br>
sudo apt-get install supervisor<br>
启动 Supervisor: sudo supervisord<br>


