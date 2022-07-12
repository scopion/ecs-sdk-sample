package com.aliyun.ecs.sample;
import com.aliyuncs.DefaultAcsClient;
import com.aliyuncs.auth.BasicCredentials;
import com.aliyuncs.auth.STSAssumeRoleSessionCredentialsProvider;
import com.aliyuncs.ecs.model.v20140526.DescribeInstancesRequest;
import com.aliyuncs.ecs.model.v20140526.DescribeInstancesResponse;
import com.aliyuncs.ecs.model.v20140526.DescribeRegionsRequest;
import com.aliyuncs.ecs.model.v20140526.DescribeRegionsResponse;
import com.aliyuncs.exceptions.ClientException;
import com.aliyuncs.http.FormatType;
import com.aliyuncs.profile.DefaultProfile;
import com.aliyuncs.slb.model.v20140515.DescribeLoadBalancerAttributeRequest;
import com.aliyuncs.slb.model.v20140515.DescribeLoadBalancerAttributeResponse;
import com.aliyuncs.slb.model.v20140515.DescribeLoadBalancersRequest;
import com.aliyuncs.slb.model.v20140515.DescribeLoadBalancersResponse;
import com.dingtalk.api.DefaultDingTalkClient;
import com.dingtalk.api.DingTalkClient;
import com.dingtalk.api.request.OapiRobotSendRequest;
import com.dingtalk.api.response.OapiRobotSendResponse;
import com.google.gson.JsonParser;

import java.io.InvalidClassException;
import java.io.UnsupportedEncodingException;
import java.net.ConnectException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.SimpleDateFormat;
import java.util.Date;
//import org.apache.commons.httpclient.HttpClient;
//import org.apache.commons.httpclient.SimpleHttpConnectionManager;
//import org.apache.commons.httpclient.methods.PostMethod;
import java.io.IOException;
import java.util.*;
import com.google.gson.Gson;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import com.taobao.api.ApiException;
import org.apache.commons.codec.binary.Base64;
import java.net.URLEncoder;

public class Ecs {
    public static void sentText(OapiRobotSendRequest request,String msg) {
        OapiRobotSendRequest.Text text = new OapiRobotSendRequest.Text();
        text.setContent(msg);
        request.setMsgtype("text");
        request.setText(text);
    }

    public static void main(String[] args){
        try{
            //统计各账号机器
            mysql db = new mysql();
            db.initagsum();
            db.initsum();
            DefaultProfile profile = DefaultProfile.getProfile("cn-hangzhou");
            BasicCredentials basicCredentials = new BasicCredentials(
                    "ertwert3",
                    "wertwegsdf"
            );
            //声明arnlist
            ResultSet arnlist = db.getarn();
            ResultSet tagoklist = db.gettags();
            String tagstr=null;
            String tagok=null;

            //身份循环开始 获取，赋值
            while (arnlist.next()) {
                String arn = arnlist.getString("arn");
                int debusid = arnlist.getInt("business_ids");
                int deopsuserid = arnlist.getInt("opsuserid");
                int debususerid = arnlist.getInt("bususerid");
                int busid = 0;
                int opsuserid = 0;
                int bususerid = 0;
                int ecssum = 0;
                int slbsum = 0;
                System.out.println("start arn is" + arn);

                try {
                    //切换身份
                    STSAssumeRoleSessionCredentialsProvider provider = new STSAssumeRoleSessionCredentialsProvider(
                            basicCredentials,
                            //引用变量
                            arn,
                            profile
                    );
                    //实例化阿里云client
                    DefaultAcsClient client = new DefaultAcsClient(profile, provider);

                    String host_position = "aliyun";
                    String strDateFormat = "yyyy-MM-dd HH:mm:ss";
                    SimpleDateFormat sdf = new SimpleDateFormat(strDateFormat);
                    //获取slb region
                    com.aliyuncs.slb.model.v20140515.DescribeRegionsRequest slbregionsRequest = new com.aliyuncs.slb.model.v20140515.DescribeRegionsRequest();
                    slbregionsRequest.setAcceptFormat(FormatType.JSON);
                    com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse slbregionsResponse = client.getAcsResponse(slbregionsRequest);
                    List<com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse.Region> slbregionList = slbregionsResponse.getRegions();
//                     String slbregionjson = new Gson().toJson(slbregionList);
//                     System.out.println("get slbregions success   "+slbregionjson);
                    //地区循环
                    for (com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse.Region slbregion : slbregionList) {
                        String slbregionId = slbregion.getRegionId();
                        System.out.println(slbregion.getRegionId());
                        DescribeLoadBalancersRequest describeLoadBalancersRequest = new DescribeLoadBalancersRequest();
                        //DescribeLoadBalancersRequest.setAcceptFormat(FormatType.JSON);
                        describeLoadBalancersRequest.setRegionId(slbregion.getRegionId());
                        DescribeLoadBalancersResponse describeLoadBalancersResponse = new DescribeLoadBalancersResponse();
                        describeLoadBalancersResponse = client.getAcsResponse(describeLoadBalancersRequest);
                        List<DescribeLoadBalancersResponse.LoadBalancer> loadBalancerList = describeLoadBalancersResponse.getLoadBalancers();
                        int slbsize = describeLoadBalancersResponse.getTotalCount();
                        slbsum = slbsum + slbsize;
                        //循环插入机器
                        for (DescribeLoadBalancersResponse.LoadBalancer loadBalancer : loadBalancerList) {
                            String loadBalancerId = loadBalancer.getLoadBalancerId();
                            String loadBalancerName = loadBalancer.getLoadBalancerName();
                            String ip = loadBalancer.getAddress();
                            String device_type = "slb";
                            String loadBalancerStatus = loadBalancer.getLoadBalancerStatus();
                            ArrayList<String> backendServerList = new ArrayList<String>();
                            DescribeLoadBalancerAttributeRequest describeLoadBalancerAttributeRequest = new DescribeLoadBalancerAttributeRequest();
                            //DescribeLoadBalancerAttributeRequest.setAcceptFormat(FormatType.JSON);
                            describeLoadBalancerAttributeRequest.setLoadBalancerId(loadBalancerId);
                            describeLoadBalancerAttributeRequest.setRegionId(slbregion.getRegionId());
                            DescribeLoadBalancerAttributeResponse describeLoadBalancerAttributeResponse = client.getAcsResponse(describeLoadBalancerAttributeRequest);
                            List<DescribeLoadBalancerAttributeResponse.BackendServer> backendServers = describeLoadBalancerAttributeResponse.getBackendServers();
                            for (DescribeLoadBalancerAttributeResponse.BackendServer backendServer : backendServers) {
                                String serverid = backendServer.getServerId();
                                backendServerList.add(serverid);
                            }
                            String backendList = "[" + String.join(",", backendServerList) + "]";
                            String networkType = loadBalancer.getNetworkType();
                            String vpcId = loadBalancer.getVpcId();
                            String createTime = loadBalancer.getCreateTime();
                            Date date = new Date();
                            String updateTime = sdf.format(date);
                            busid = debusid;
                            opsuserid = deopsuserid;
                            bususerid = debususerid;
                            //db.updateslb(loadBalancerId,ip,loadBalancerName,loadBalancerStatus,backendServerList.toString(),regionId,networkType,vpcId,createTime,arn);
                            db.updatecms_host_slb(loadBalancerId, loadBalancerName, ip, device_type, host_position, slbregionId, updateTime, loadBalancerStatus, arn, busid, opsuserid, bususerid, backendList, networkType, vpcId, createTime);
                        }
                        System.out.println(arn + " slb in " + slbregion.getRegionId() + " is done");

                    }



                    //获取所有地区
                    System.out.println("start get ecs region");
                    DescribeRegionsRequest regionsRequest = new DescribeRegionsRequest();
                    regionsRequest.setAcceptFormat(FormatType.JSON);
                    DescribeRegionsResponse regionsResponse = client.getAcsResponse(regionsRequest);
                    List<DescribeRegionsResponse.Region> regionList = regionsResponse.getRegions();
//                    System.out.println("get regions success   ");
                    int ecscount = 0;


                    //地区循环
                    for (DescribeRegionsResponse.Region region : regionList) {
                        System.out.println(region.getRegionId());
                        String regionId = region.getRegionId();
                        //获取地区里的ECS
                        DescribeInstancesRequest describeInstancesRequest = new DescribeInstancesRequest();
                        describeInstancesRequest.setAcceptFormat(FormatType.JSON);
                        describeInstancesRequest.setRegionId(region.getRegionId());
                        //获取地区机器总数,并判断是否插入数据库
                        ecscount = client.getAcsResponse(describeInstancesRequest).getTotalCount();
                        System.out.println(region.getRegionId() + "  " + ecscount);
                        ecssum = ecssum + ecscount;
                        if (ecscount == 0) {
                            //当前地区没有机器，下个地区
                            System.out.println("there is no Instances in " + region.getRegionId() + " region   ");
                        } else {
                            int PageNumber;
                            int size = 10;
                            //循环读取不同页
                            for (PageNumber = 1; size >= 10; PageNumber++) {
                                //获取当前页机器列表
                                describeInstancesRequest.setPageNumber(PageNumber);
                                describeInstancesRequest.setPageSize(10);
                                DescribeInstancesResponse describeInstancesResponse = client.getAcsResponse(describeInstancesRequest);
                                List<DescribeInstancesResponse.Instance> instanceList = describeInstancesResponse.getInstances();
                                size = instanceList.size();
                                //判断运维账号
                                if (arn.equals("acs:ram::16419wert3453e/ewet-security")) {
                                    for (DescribeInstancesResponse.Instance instance : instanceList) {
                                        //循环插入机器
//                                 String instancejson= new Gson().toJson(instance);
//                                 System.out.println(instancejson);
                                        String instanceId = instance.getInstanceId();
                                        String instanceName = instance.getInstanceName();
                                        List privateIpAddresslist = instance.getVpcAttributes().getPrivateIpAddress();
                                        String vpcId = instance.getVpcAttributes().getVpcId();
                                        String eipAddress = instance.getEipAddress().getIpAddress();
                                        String device_type = "eip";
                                        if (eipAddress.isEmpty()) {
                                            device_type = "ip";
                                        }
                                        List innerIpAddresslist = instance.getInnerIpAddress();
                                        List publicIpAddresslist = instance.getPublicIpAddress();
                                        String privateIpAddress = "";
                                        String publicIpAddress = "";
                                        if (innerIpAddresslist.isEmpty()) {
                                            privateIpAddress = privateIpAddresslist.get(0).toString();
                                        } else {
                                            privateIpAddress = innerIpAddresslist.get(0).toString();
                                        }
                                        if (publicIpAddresslist.isEmpty()) {
                                            publicIpAddress = "";
                                        } else {
                                            publicIpAddress = publicIpAddresslist.get(0).toString();
                                        }
                                        String OSName = instance.getOSName();
                                        String serialNumber = instance.getSerialNumber();
                                        Date date = new Date();
                                        String updateTime = sdf.format(date);
                                        String status = instance.getStatus();
                                        String networkType = instance.getInstanceNetworkType();
                                        String createTime = instance.getCreationTime();
                                        String tagcheck = "false";
                                        ArrayList<String> taglist = new ArrayList<String>();
                                        List<DescribeInstancesResponse.Instance.Tag> tags = instance.getTags();
                                        if (tags.isEmpty()) {
                                            tagstr = null;
//                                            for (String tagname :tagoklist){
//                                                if(instanceName.contains(tagname)){
//                                                    tagcheck="true";
//                                                    break;
//                                                }
//                                            }
                                        } else {
                                            for (DescribeInstancesResponse.Instance.Tag tag : tags) {
//                                            System.out.println("将tag加入列表");
                                                taglist.add(tag.getTagKey());
                                            }
                                            //判断标签与业务线
                                            while (tagoklist.next()) {
                                                tagok = tagoklist.getString("tag");
                                                if (taglist.contains(tagok)) {
                                                    System.out.println(tagok + "存在");
                                                    busid = tagoklist.getInt("busid");
                                                    opsuserid = tagoklist.getInt("opsuserid");
                                                    bususerid = tagoklist.getInt("bususerid");
                                                    db.updatetagsum(tagok);
                                                    tagcheck = "true";
                                                    break;
                                                } else {
                                                    busid = debusid;
                                                    opsuserid = deopsuserid;
                                                    bususerid = debususerid;
                                                }
                                            }
                                            tagoklist.beforeFirst();
                                            tagstr = "['" + String.join("','", taglist) + "']";
                                        }
                                        System.out.println(arn + " bus: " + busid + " opsuser: " + opsuserid + " bususer: " + bususerid);
                                        //System.out.println(instanceId);
                                        //System.out.println(tagstr);
                                        db.updatecloudhost(instanceId, tagstr, tagcheck, instanceName, privateIpAddress, publicIpAddress, eipAddress, host_position, OSName, regionId, serialNumber, updateTime, status, arn);
                                        db.updatecms_host(instanceId, instanceName, privateIpAddress, publicIpAddress, eipAddress, device_type, host_position, OSName, regionId, serialNumber, updateTime, status, arn, tagstr, busid, opsuserid, bususerid, networkType, vpcId, createTime);
                                    }
                                } else {
                                    System.out.println("no jituan-security");
                                    System.out.println(arn + " bus: " + debusid + " opsuser: " + deopsuserid + " bususer: " + debususerid);
                                    for (DescribeInstancesResponse.Instance instance : instanceList) {
                                        //循环插入机器
//                                        String instancejson= new Gson().toJson(instance);
//                                        System.out.println(instancejson);
                                        String instanceId = instance.getInstanceId();
                                        String instanceName = instance.getInstanceName();
                                        List privateIpAddresslist = instance.getVpcAttributes().getPrivateIpAddress();
                                        String vpcId = instance.getVpcAttributes().getVpcId();
                                        String eipAddress = instance.getEipAddress().getIpAddress();
                                        String device_type = "eip";
                                        if (eipAddress.isEmpty()) {
                                            device_type = "ip";
                                        }
                                        List innerIpAddresslist = instance.getInnerIpAddress();
                                        List publicIpAddresslist = instance.getPublicIpAddress();
                                        String privateIpAddress = "";
                                        String publicIpAddress = "";
                                        if (innerIpAddresslist.isEmpty()) {
                                            privateIpAddress = privateIpAddresslist.get(0).toString();
                                        } else {
                                            privateIpAddress = innerIpAddresslist.get(0).toString();
                                        }
                                        if (publicIpAddresslist.isEmpty()) {
                                            publicIpAddress = "";
                                        } else {
                                            publicIpAddress = publicIpAddresslist.get(0).toString();
                                        }
                                        String OSName = instance.getOSName();
                                        String serialNumber = instance.getSerialNumber();
                                        Date date = new Date();
                                        String updateTime = sdf.format(date);
                                        String status = instance.getStatus();
                                        String networkType = instance.getInstanceNetworkType();
                                        String createTime = instance.getCreationTime();
                                        String tagcheck = "true";
                                        ArrayList<String> taglist = new ArrayList<String>();
                                        List<DescribeInstancesResponse.Instance.Tag> tags = instance.getTags();
                                        if (tags.isEmpty()) {
                                            tagstr = null;
                                        } else {
                                            for (DescribeInstancesResponse.Instance.Tag tag : tags) {
//                                            System.out.println("将tag加入列表");
                                                taglist.add(tag.getTagKey());
                                            }
                                            tagstr = "['" + String.join("','", taglist) + "']";
                                        }
//                                        System.out.println(arn+" bus: "+busid+" opsuser: "+opsuserid+" bususer: "+bususerid);
                                        //System.out.println(tagstr);
                                        db.updatecloudhost(instanceId, tagstr, tagcheck, instanceName, privateIpAddress, publicIpAddress, eipAddress, host_position, OSName, regionId, serialNumber, updateTime, status, arn);
                                        db.updatecms_host(instanceId, instanceName, privateIpAddress, publicIpAddress, eipAddress, device_type, host_position, OSName, regionId, serialNumber, updateTime, status, arn, tagstr, debusid, deopsuserid, debususerid, networkType, vpcId, createTime);
                                    }
                                }
                                System.out.println("pages " + PageNumber + " done");
                            }
                        }
                        System.out.println(arn+"instance in " + region.getRegionId() + " is done");
                    }

                    System.out.println(ecssum+" "+slbsum);

                    db.updatenum(ecssum, slbsum,arn);

                } catch (ClientException cliente) {
                    cliente.printStackTrace();
                    System.err.println(cliente);
                    System.out.println(arn + "    ClientException:" + cliente);
                }
                //当前身份结束
                System.out.println(arn +" is done");
            }

            //身份循环结束
            System.out.println("all arn is end");
            db.delcloudhost();
            //db.delslb();
            db.delcms_hosts();
            db.close();
            System.out.println("job is done");
            try{
                Long timestamp = System.currentTimeMillis();
                String yachurl = "https://yacwerou.com/robot/send?access_token=OHpuTnowertWVlUMlRRS3B0elNwSTN6R0wertKw";
                String secret = "SEwert20a79e9";
                String stringToSign = timestamp + "\n" + secret;
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(secret.getBytes("UTF-8"), "HmacSHA256"));
                byte[] signData = mac.doFinal(stringToSign.getBytes("UTF-8"));
                String sign = URLEncoder.encode(new String(Base64.encodeBase64(signData)),"UTF-8");
                String webhook = yachurl + "&timestamp=" + timestamp.toString() + "&sign=" + sign;
/////////          System.out.println(webhook);
                DingTalkClient dingTalkClient = new DefaultDingTalkClient(webhook);
                OapiRobotSendRequest request = new OapiRobotSendRequest();
                OapiRobotSendRequest.At at = new OapiRobotSendRequest.At();
                // 若上一步isAtAll没有设置true，则根据此处设置的手机号来@指定人
                List<String> mobiles = new ArrayList<>();
                mobiles.add("1wertrt26");
                at.setAtMobiles(mobiles);
                at.setIsAtAll(false);
                request.setAt(at);
                String errmsg = "ecs-sdk-sample:aliyun资产获取正常运行 @18wert34526";
//                System.err.println(errmsg);
                // 以下是设置各种消息格式的方法
                sentText(request,errmsg);
                //    sendLink(request);
                //    sendMarkdown(request);
                //    sendActionCard(request);
                //    sendFeedCard(request);
                OapiRobotSendResponse response = dingTalkClient.execute(request);
                System.out.println(response.getErrmsg());
            } catch (Exception dinge) {
                System.out.println("Exception:" + dinge.toString());
            }

        } catch (Exception e){
            try{
                Long timestamp = System.currentTimeMillis();
                String yachurl = "https://ywer.com/robot/send?access_token=OHpuTno4LwertYlcxcEZ4MmE4WVlU2530lrVV4IKw";
                String secret = "SEC23fsdgfertea79e9";
                String stringToSign = timestamp + "\n" + secret;
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(secret.getBytes("UTF-8"), "HmacSHA256"));
                byte[] signData = mac.doFinal(stringToSign.getBytes("UTF-8"));
                String sign = URLEncoder.encode(new String(Base64.encodeBase64(signData)),"UTF-8");
                String webhook = yachurl + "&timestamp=" + timestamp.toString() + "&sign=" + sign;
/////////          System.out.println(webhook);
                DingTalkClient dingTalkClient = new DefaultDingTalkClient(webhook);
                OapiRobotSendRequest request = new OapiRobotSendRequest();
                OapiRobotSendRequest.At at = new OapiRobotSendRequest.At();
                // 若上一步isAtAll没有设置true，则根据此处设置的手机号来@指定人
                List<String> mobiles = new ArrayList<>();
                mobiles.add("18234523426");
                at.setAtMobiles(mobiles);
                at.setIsAtAll(false);
                request.setAt(at);
                String errmsg = "ecs-sdk-sample:SQLException "+e.toString()+" @18023453456";
                System.err.println(errmsg);
                // 以下是设置各种消息格式的方法
                sentText(request,errmsg);
                //    sendLink(request);
                //    sendMarkdown(request);
                //    sendActionCard(request);
                //    sendFeedCard(request);
                OapiRobotSendResponse response = dingTalkClient.execute(request);
                System.out.println(response.getErrmsg());
            } catch (Exception dinge) {
                System.out.println("Exception:" + dinge.toString());
            }

        }

    }

}


