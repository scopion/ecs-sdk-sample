#! /bin/bash
set -ex
cd /opt/yuncloud/ecs-sdk-sample
python getucloud.py > ucloud.log &
#python getqingcloud.py > qingcloud.log &
mvn -q exec:java -Dexec.mainClass=com.aliyun.ecs.sample.Ecs > ecs.log &
