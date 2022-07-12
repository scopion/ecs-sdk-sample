package com.aliyun.ecs.sample;


import java.io.FileInputStream;
import java.io.InputStream;
import java.sql.*;
import java.util.ArrayList;
import java.util.Properties;

public class mysql {
    //服务器限制连接。代码能用。

    private static final String PROPERTIES_NAME = "db.properties";
    public static String name = null;
    public static String url = null;
    public static String user = null;
    public static String password = null;

    static{
        FileInputStream in = null;
        try{
            // 使用ClassLoader加载properties配置文件生成对应的输入流
            in = new FileInputStream(PROPERTIES_NAME);
            // 使用properties对象加载输入流
            System.out.println(in);
            Properties properties = new Properties();
            properties.load(in);
            name = properties.getProperty("name");
            url = properties.getProperty("url");
            user = properties.getProperty("user");
            password = properties.getProperty("password");
            System.out.println("读取配置信息成功！");
        }catch(Exception e){
            e.printStackTrace();
            System.out.println("读取配置信息失败！");
        }finally{
            if(in != null){
                try{
                    in.close();
                }catch(Exception e){
                    e.printStackTrace();
                }
            }
        }
    }
    public Connection connection = null;
    public PreparedStatement preparedStatement = null;

//方法都用throws，去掉catch。
    public mysql() throws Exception  {
//        try {
            Class.forName(name);// 指定连接类型
            connection = DriverManager.getConnection(url, user, password);// 获取连接
//            pst = conn.prepareStatement(sql);// 准备执行语句
//        } catch (Exception e){
//            e.printStackTrace();
//        }
    }


    public void close() throws Exception{
    /**
     *
     * 方法名称: close ；
     * 方法描述:  关闭数据库连接 ；
     * 参数 ：
     * 返回类型: void ；
     **/
//        try {
            this.connection.close();
            this.preparedStatement.close();
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
    }

    public boolean initsum() throws Exception{
        boolean flag = false;
        String sql = "UPDATE authorization_arners SET instancenum = 0 where type ='aliyun'";
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            int result = preparedStatement.executeUpdate();
//            System.out.println("初始化tag服务器数量");
            flag=true;
//        } catch (Exception e) {
//            System.out.println("init authorization_tags nums error！！");
//            e.printStackTrace();
//        }
        return  flag;
    }

    public boolean updatenum(int num,int slbnum,String arn) throws Exception{
        boolean flag = false;
        String sql = "UPDATE authorization_arners SET instancenum = ? ,slbnum = ? WHERE arn = ? ";
//        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.setInt(1,num);
            preparedStatement.setInt(2,slbnum);
            preparedStatement.setString(3,arn);
            int result = preparedStatement.executeUpdate();
//            System.out.println("更新服务器数量");
            flag=true;
//        } catch (Exception e) {
//            System.out.println("UPDATE authorization_arners error！！");
//            e.printStackTrace();
//        }
        return  flag;
    }

    public boolean initagsum() throws  Exception{
        boolean flag = false;
        String sql = "UPDATE authorization_tags SET sum = 0";
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            int result = preparedStatement.executeUpdate();
//            System.out.println("初始化tag服务器数量");
            flag=true;
//        } catch (Exception e) {
//            System.out.println("init authorization_tags nums error！！");
//            e.printStackTrace();
//        }
        return  flag;
    }

    public boolean updatetagsum(String tag) throws Exception{
        boolean flag = false;
        String sql = "UPDATE authorization_tags SET sum = sum+1 where tag =? ";
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            preparedStatement.setString(1,tag);
//            preparedStatement.setString(2,arn);
            int result = preparedStatement.executeUpdate();
            //System.out.println("更新tag服务器数量");
            flag=true;
//        } catch (Exception e) {
//            System.out.println("UPDATE authorization_tags nums error！！");
//            e.printStackTrace();
//        }
        return  flag;
    }

    public void updatecms_host(String instanceId,String instanceName,String privateIpAddress,String publicIpAddress,String eipAddress,String device_type,String host_position,String OSName,String regionId,String serialNumber,String updateTime,String status,String arn,String tags,int  busid,int opsuserid,int bususerid,String networkType,String vpcId,String createTime) throws Exception{
        //要执行的SQL
        String sql = "insert into cms_hosts(instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,device_type,host_position,OSName,regionId,serialNumber,updateTime,ip_updateflag,status,arn,tags,busid,opsuserid,bususerid,networkType,vpcId,createTime) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on duplicate key update instanceName=VALUES(instanceName),privateIpAddress=VALUES(privateIpAddress),publicIpAddress=VALUES(publicIpAddress),eipAddress=VALUES(eipAddress),device_type=VALUES(device_type),host_position=VALUES(host_position),OSName=VALUES(OSName),regionId=VALUES(regionId),serialNumber=VALUES(serialNumber),updateTime=VALUES(updateTime),ip_updateflag=VALUES(ip_updateflag),status=VALUES(status),arn=VALUES(arn),tags=VALUES(tags),busid=VALUES(busid),opsuserid=VALUES(opsuserid),bususerid=VALUES(bususerid),networkType=VALUES(networkType),vpcId=VALUES(vpcId),createTime=VALUES(createTime)";
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            preparedStatement.setString(1,instanceId);
            preparedStatement.setString(2,instanceName);
            preparedStatement.setString(3,privateIpAddress);
            preparedStatement.setString(4,publicIpAddress);
            preparedStatement.setString(5,eipAddress);
            preparedStatement.setString(6,device_type);
            preparedStatement.setString(7,host_position);
            preparedStatement.setString(8,OSName);
            preparedStatement.setString(9,regionId);
            preparedStatement.setString(10,serialNumber);
            preparedStatement.setString(11,updateTime);
            preparedStatement.setString(12,updateTime);
            preparedStatement.setString(13,status);
            preparedStatement.setString(14,arn);
            preparedStatement.setString(15,tags);
            preparedStatement.setInt(16,busid);
            preparedStatement.setInt(17,opsuserid);
            preparedStatement.setInt(18,bususerid);
            preparedStatement.setString(19,networkType);
            preparedStatement.setString(20,vpcId);
            preparedStatement.setString(21,createTime);

            int result = preparedStatement.executeUpdate();

            if (result>0){
                //System.out.println("updatesuccess");}
            }
            else{System.out.println("update cms_hosts fail");}

//        } catch (Exception e) {
//            e.printStackTrace();
//        }


    }

    public void updatecms_host_slb(String instanceId,String instanceName,String publicIpAddress,String device_type,String host_position,String regionId,String updateTime,String status,String arn,int  busid,int opsuserid,int bususerid,String backendList,String networkType,String vpcId,String createTime) throws Exception{
        //要执行的SQL
        String sql = "insert into cms_hosts(instanceId,instanceName,publicIpAddress,device_type,host_position,regionId,updateTime,ip_updateflag,status,arn,busid,opsuserid,bususerid,backendList,networkType,vpcId,createTime) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) on duplicate key update instanceName=VALUES(instanceName),publicIpAddress=VALUES(publicIpAddress),device_type=VALUES(device_type),host_position=VALUES(host_position),regionId=VALUES(regionId),updateTime=VALUES(updateTime),ip_updateflag=VALUES(ip_updateflag),status=VALUES(status),arn=VALUES(arn),busid=VALUES(busid),opsuserid=VALUES(opsuserid),bususerid=VALUES(bususerid),backendList=VALUES(backendList),networkType=VALUES(networkType),vpcId=VALUES(vpcId),createTime=VALUES(createTime)";
//        try {
        preparedStatement = connection.prepareStatement(sql); // 准备执行语句
        preparedStatement.setString(1,instanceId);
        preparedStatement.setString(2,instanceName);
        preparedStatement.setString(3,publicIpAddress);
        preparedStatement.setString(4,device_type);
        preparedStatement.setString(5,host_position);
        preparedStatement.setString(6,regionId);
        preparedStatement.setString(7,updateTime);
        preparedStatement.setString(8,updateTime);
        preparedStatement.setString(9,status);
        preparedStatement.setString(10,arn);
        preparedStatement.setInt(11,busid);
        preparedStatement.setInt(12,opsuserid);
        preparedStatement.setInt(13,bususerid);
        preparedStatement.setString(14,backendList);
        preparedStatement.setString(15,networkType);
        preparedStatement.setString(16,vpcId);
        preparedStatement.setString(17,createTime);

        int result = preparedStatement.executeUpdate();

        if (result>0){
            //System.out.println("updatesuccess");}
        }
        else{System.out.println("update cms_hosts fail");}

//        } catch (Exception e) {
//            e.printStackTrace();
//        }


    }


    public void updatecloudhost(String instanceId,String tags,String tagcheck,String instanceName,String privateIpAddress,String publicIpAddress,String eipAddress,String OSNEnvironment,String OSName,String regionId,String serialNumber,String updateTime,String status,String arn) throws Exception{

        //要执行的SQL
        String sql = "insert into cloudhost(instanceId,instanceName,privateIpAddress,publicIpAddress,eipAddress,OSNEnvironment,OSName,regionId,serialNumber,updateTime,status,arn,tags,tagcheck) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?) on duplicate key update instanceName=VALUES(instanceName),privateIpAddress=VALUES(privateIpAddress),publicIpAddress=VALUES(publicIpAddress),eipAddress=VALUES(eipAddress),OSNEnvironment=VALUES(OSNEnvironment),OSName=VALUES(OSName),regionId=VALUES(regionId),serialNumber=VALUES(serialNumber),updateTime=VALUES(updateTime),status=VALUES(status),arn=VALUES(arn),tags=VALUES(tags),tagcheck=VALUES(tagcheck)";

//        try {

            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            preparedStatement.setString(1,instanceId);
            preparedStatement.setString(2,instanceName);
            preparedStatement.setString(3,privateIpAddress);
            preparedStatement.setString(4,publicIpAddress);
            preparedStatement.setString(5,eipAddress);
            preparedStatement.setString(6,OSNEnvironment);
            preparedStatement.setString(7,OSName);
            preparedStatement.setString(8,regionId);
            preparedStatement.setString(9,serialNumber);
            preparedStatement.setString(10,updateTime);
            preparedStatement.setString(11,status);
            preparedStatement.setString(12,arn);
            preparedStatement.setString(13,tags);
            preparedStatement.setString(14,tagcheck);

            int result = preparedStatement.executeUpdate();

            if (result>0){
                //System.out.println("updatesuccess");}
            }
            else{System.out.println("update cloudhost fail");}

//        } catch (Exception e) {
//            e.printStackTrace();
//        }


    }

    public void updateslb(String loadBalancerId,String ip ,String loadBalancerName ,String loadBalancerStatus ,String backendServerList,String regionId , String networkType ,String vpcId ,String createTime,String arn) throws Exception{

        //要执行的SQL
        String sql = "insert into aliyunslb(loadBalancerId,ip,loadBalancerName,loadBalancerStatus,backendServerList,regionId,networkType,vpcId,createTime,arn) values(?,?,?,?,?,?,?,?,?,?) on duplicate key update ip=VALUES(ip),loadBalancerName=VALUES(loadBalancerName),loadBalancerStatus=VALUES(loadBalancerStatus),backendServerList=VALUES(backendServerList),regionId=VALUES(regionId),networkType=VALUES(networkType),vpcId=VALUES(vpcId),createTime=VALUES(createTime),arn=VALUES(arn)";
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            preparedStatement.setString(1,loadBalancerId);
            preparedStatement.setString(2,ip);
            preparedStatement.setString(3,loadBalancerName);
            preparedStatement.setString(4,loadBalancerStatus);
            preparedStatement.setString(5,backendServerList);
            preparedStatement.setString(6,regionId);
            preparedStatement.setString(7,networkType);
            preparedStatement.setString(8,vpcId);
            preparedStatement.setString(9,createTime);
            preparedStatement.setString(10,arn);
            //preparedStatement.setString(12,arn);
            int result = preparedStatement.executeUpdate();

//            ResultSet rs = preparedStatement.executeQuery(sql);

            if (result>0){
                //System.out.println("updatesuccess");
            }
            else{System.out.println("update fail");}

//        } catch (Exception e) {
//            e.printStackTrace();
//            System.out.println("update sql fail");
//        }

    }


    public void delcms_hosts() throws Exception{
        String sql = "delete from cms_hosts WHERE host_position='aliyun' and DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d');";

//        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.executeUpdate();

//        } catch (Exception e){
//            System.out.println("delete from cms_hosts error！！");
//            e.printStackTrace();
//        }
    }

    public void delcloudhost() throws  Exception{
        String sql = "delete from cloudhost WHERE OSNEnvironment ='aliyun' and DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d');";

//        try {
            preparedStatement = connection.prepareStatement(sql);
            preparedStatement.executeUpdate();
//        } catch (Exception e) {
//            System.out.println("delete from cloudhost error！！");
//            e.printStackTrace();
//        }
    }

    public void delslb() throws  Exception{
        String sql = "delete from aliyunslb WHERE DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d');";

//        try {
        preparedStatement = connection.prepareStatement(sql);
        preparedStatement.executeUpdate();
//        } catch (Exception e) {
//            System.out.println("delete from cloudhost error！！");
//            e.printStackTrace();
//        }
    }


    public ResultSet getarn() throws  Exception{
        String sql = "SELECT arn,business_ids,bususerid,opsuserid FROM `authorization_arners` WHERE type='aliyun'";
        ResultSet result =null;
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            result = preparedStatement.executeQuery();
//////            while(result.next()){
//////                arnlist.add(result.getString(1));
/// ///           }
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
        return  result;
    }

    public ResultSet gettags() throws Exception{
        String sql = "SELECT tag,busid,bususerid,opsuserid FROM `authorization_tags` ";
        ResultSet result = null;
//        try {
            preparedStatement = connection.prepareStatement(sql); // 准备执行语句
            result = preparedStatement.executeQuery();
//////            while(result.next()){
//////                taglist.add(result.getString("tag"));
//////            }
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
        return  result;
    }

}
