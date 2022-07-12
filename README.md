# aliyunEcs
maven 项目  

getucloud.py 为获取Ucloud所有服务器  
getqingcloud.py 为获取青云所有服务器  
主要用于建立自己的资产库，梳理资产情况，核对归属业务等，用于对全资产服务器端口的扫描  

aliyun 获取阿里云云服务器

### 编译及运行指令
> mvn clean package -Dmaven.test.skip=true install
> mvn -q exec:java -Dexec.mainClass=com.aliyun.ecs.sample.Ecs

### 计划任务
> 0 5  * * * /usr/bin/bash /opt/yuncloud/aegis-sdk-sample/run.sh > /opt/yuncloud/aegis.log &
