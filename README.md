=在本地环境中运行console的步骤：
1. 配置本地sql数据库、redis数据库，在config.ini配置文件中把数据库配置为本地  
2. 修改项目配置文件  
    1) 在conf文件夹中，复制config_sample.ini文件，并把新文件命名为config.ini
    2) 在当前目录下创建db116.sqlit3文件 `touch db11.sqlit3`
    3) 修改config.ini文件中的database设置,把db_name路径修改为本地路径
    4) 修改config.ini文件中的statics设置，把static_root和media_root修改为当前用户可写的文件夹
    5) 修改config.ini文件中的zone_map设置

      ```shell
       bj = http://192.168.5.20:7701
       yz = http://192.168.5.20:7701
       drs = http://192.168.5.20:7701
       policy = http://192.168.5.20:7701
       license = http://192.168.5.20:7701
      ```

3. 同步数据库表单  
    先执行

    ```shell
    python manage.py migrate auth
    ```

    在项目根目录下执行

    ```shell
    python manage.py migrate
    ```

4. 进行数据初始化,在根目录下执行以下命令  

    ```python
    ./manage.py import_zones bj not 
    ./manage.py import_zones all not 
    ./manage.py import_images bj not
    ./manage.py import_flavors not
    ./manage.py import_quotas bj not
    ./manage.py createsuperuser #必须创建名为root的用户,以便后续import_xxx类的方法可用
    python manage.py import_ip_pool not
    ./manage.py init_permission
    ./manage.py import_role
    ```

**3和4可以通过运行命令`sh scripts/import.sh`一次完成**

5. 创建本地用户  

    ```shell
    ./manage.py createadminaccount
    ```

6. 启动项目服务，在根目录下执行  

    ```shell
    python manage.py runserver
    ```

    之后在浏览器中访问127.0.0.1:8000即可在本地运行console项目

需要的license 为：
   `i31PaFNqSSWpug9G0YhXlua4RaS9LR5mdGl/iBtoD/hcY0SgwWcT1Pym2i4qS9lbeqy9YdB53Rc6Y2S6FvldTkan64Mw7pAK9jSiP6NSDe67Wrdvrf6LVczIu5I2ZU2QhtSAbHrFANgyKRYMwdhhf7jWIRCFdPRjR3F9g4NQbsY=`



=私有云在联调环境中的部署  

    联调环境中私有云的部署主要使用了supervisor  

==初次部署步骤如下：  

    在192.168.2.15/opt/console/console目录下运行如下命令  

    ```shell
    (supervisord -c conf/supervisor.ini &)
    ```

==有代码的时候重启服务：  

    1. 在192.168.2.15/opt/console/console和192.168.2.15/opt/console/console_admin中, 以及192.168.2.16/var/www/statics/console分别git pull upstream dev-debug2.0  
    2. 在192.168.2.15/opt/console/console文件夹下运行  

    ```shell
    supervisorctl -c conf/supervisor.ini restart console
    supervisorctl -c conf/supervisor.ini restart console_admin
    ```

    然后通过192.168.2.20可以访问私有云console，通过192.168.2.15:8001可以访问console_admin
