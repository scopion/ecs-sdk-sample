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
import com.google.gson.Gson;
import org.apache.commons.codec.binary.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.URLEncoder;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;


public class App {
    public static void sentText(OapiRobotSendRequest request, String msg) {
        OapiRobotSendRequest.Text text = new OapiRobotSendRequest.Text();
        text.setContent(msg);
        request.setMsgtype("text");
        request.setText(text);
    }

    public static void main(String[] args){
         ///// throws ConnectException,ClientException NoSuchAlgorithmException,UnsupportedEncodingException,InvalidKeyException,ApiException
         try{
             mysql db = new mysql();
             ResultSet arnlist = db.getarn();
             ResultSet tagoklist = db.gettags();
             System.out.println("test");
             DefaultProfile profile = DefaultProfile.getProfile("cn-hangzhou");
             BasicCredentials basicCredentials = new BasicCredentials(
                     "ertwert",
                     "wert34563456"
             );
             int sum = 0;
             int slbsum = 0;
             String tagstr=null;
             String tagok=null;
             //身份循环开始 获取，赋值
             while (arnlist.next()) {
                 System.out.println("test1");
                 int count;
                 String arn = arnlist.getString("arn");
                 //system
                 int debusid = arnlist.getInt("business_ids");
                 int deopsuserid = arnlist.getInt("opsuserid");
                 int debususerid = arnlist.getInt("bususerid");
                 int busid = 0;
                 int opsuserid =0;
                 int bususerid = 0;
                 //System.out.println(arn);
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

                     //获取slb region
                     com.aliyuncs.slb.model.v20140515.DescribeRegionsRequest slbregionsRequest = new com.aliyuncs.slb.model.v20140515.DescribeRegionsRequest();
                     slbregionsRequest.setAcceptFormat(FormatType.JSON);

                     com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse slbregionsResponse = client.getAcsResponse(slbregionsRequest);
                     List<com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse.Region> slbregionList =slbregionsResponse.getRegions();
//                     String slbregionjson = new Gson().toJson(slbregionList);
//                     System.out.println("get slbregions success   "+slbregionjson);
                     //地区循环
                     for (com.aliyuncs.slb.model.v20140515.DescribeRegionsResponse.Region slbregion : slbregionList) {
                         System.out.println(slbregion.getRegionId());

                         DescribeLoadBalancersRequest describeLoadBalancersRequest = new DescribeLoadBalancersRequest();
                         //DescribeLoadBalancersRequest.setAcceptFormat(FormatType.JSON);
                         describeLoadBalancersRequest.setRegionId(slbregion.getRegionId());
                         DescribeLoadBalancersResponse describeLoadBalancersResponse = new DescribeLoadBalancersResponse();
                         System.out.println("|-->Get slb start.");
                         describeLoadBalancersResponse = client.getAcsResponse(describeLoadBalancersRequest);
                         System.out.println(describeLoadBalancersResponse.getRequestId());
                         List<DescribeLoadBalancersResponse.LoadBalancer> loadBalancerList = describeLoadBalancersResponse.getLoadBalancers();
                         int slbsize = describeLoadBalancersResponse.getTotalCount();
                         System.out.println("slb num" + "\t" + slbregion.getRegionId() + "\t" + slbsize);
                         slbsum = slbsum + slbsize;
                         //循环插入机器
                         for (DescribeLoadBalancersResponse.LoadBalancer loadBalancer : loadBalancerList) {
                             String loadBalancerId = loadBalancer.getLoadBalancerId();
                             String ip = loadBalancer.getAddress();
                             String loadBalancerName = loadBalancer.getLoadBalancerName();
                             String loadBalancerStatus = loadBalancer.getLoadBalancerStatus();

                             ArrayList<String> backendServerList = new ArrayList<String>();
                             DescribeLoadBalancerAttributeRequest describeLoadBalancerAttributeRequest = new DescribeLoadBalancerAttributeRequest();
                             //DescribeLoadBalancerAttributeRequest.setAcceptFormat(FormatType.JSON);
                             describeLoadBalancerAttributeRequest.setLoadBalancerId(loadBalancerId);
                             describeLoadBalancerAttributeRequest.setRegionId(slbregion.getRegionId());
                             DescribeLoadBalancerAttributeResponse describeLoadBalancerAttributeResponse = client.getAcsResponse(describeLoadBalancerAttributeRequest);
                             List<DescribeLoadBalancerAttributeResponse.BackendServer> backendServers = describeLoadBalancerAttributeResponse.getBackendServers();
                             //int backsize = backendServers.size();
                             for (DescribeLoadBalancerAttributeResponse.BackendServer backendServer : backendServers) {
                                 String serverid = backendServer.getServerId();
                                 backendServerList.add(serverid);
                             }
                             String backendList = "[" + String.join(",", backendServerList) + "]";
                             String regionId = loadBalancer.getRegionId();
                             String networkType = loadBalancer.getNetworkType();
                             String vpcId = loadBalancer.getVpcId();
                             String createTime = loadBalancer.getCreateTime();
                         }
                     }

                     //获取所有地区
                     DescribeRegionsRequest regionsRequest = new DescribeRegionsRequest();
                     regionsRequest.setAcceptFormat(FormatType.JSON);

                     DescribeRegionsResponse regionsResponse = client.getAcsResponse(regionsRequest);
                     System.out.println("requestid"+regionsResponse.getRequestId());
                     List<DescribeRegionsResponse.Region> regionList = regionsResponse.getRegions();
//                     String regionjson= new Gson().toJson(regionList);
//                     System.out.println("get regions success   "+regionjson);
                     //地区循环
                     for (DescribeRegionsResponse.Region region : regionList){
                         System.out.println(region.getRegionId());


                             //System.out.println(region.getRegionId());
                         System.out.println("get ecs start");
                         DescribeInstancesRequest describeInstancesRequest = new DescribeInstancesRequest();
                         describeInstancesRequest.setAcceptFormat(FormatType.JSON);
                         //describeInstancesRequest.setRegionId("cn-beijing");
                         describeInstancesRequest.setRegionId(region.getRegionId());
                         count = client.getAcsResponse(describeInstancesRequest).getTotalCount();
                         System.out.println("ecs num"+region.getRegionId()+"  " + count);
                         sum = sum + count;

                         if (count == 0) {
                             //当前地区没有机器，下个地区
                             System.out.println("there is no Instances in " + region.getRegionId() + " region   ");
                         } else {
                             int PageNumber;
                             int size = 10;
                             //循环读取不同页
//                             for (PageNumber = 1; size >= 10; PageNumber++) {
//                                 //获取当前页机器列表
//                                 describeInstancesRequest.setPageNumber(PageNumber);
//                                 describeInstancesRequest.setPageSize(10);
//                                 DescribeInstancesResponse describeInstancesResponse = client.getAcsResponse(describeInstancesRequest);
////                                 System.out.println(describeInstancesResponse.getRequestId());
//                                 List<DescribeInstancesResponse.Instance> instanceList = describeInstancesResponse.getInstances();
//                                 size = instanceList.size();
//                                 /////循环插入机器
//                                 if (arn.equals("acs:ram::wert335234523462:role/2345-security")){
//                                     for (DescribeInstancesResponse.Instance instance : instanceList) {
//                                         ArrayList<String> taglist = new ArrayList<String>();
//                                         String tagcheck = "false";
//                                         String jsonstr1 = new Gson().toJson(instance);
//                                         System.out.println(jsonstr1);
//                                         List<DescribeInstancesResponse.Instance.Tag> tags = instance.getTags();
//                                         String eipAddress = instance.getEipAddress().getIpAddress();
////                                         System.out.println(eipAddress);
////                                         System.out.println(eipAddress.isEmpty());
//                                         if (tags.isEmpty()){
////                                             System.out.println("tag is null");
////                                             tagstr = null;
////                                             for (String tagname :tagoklist){
////                                                 if(instanceName.contains(tagname)){
////                                                     tagcheck="true";
////                                                     break;
////                                                 }
////                                             }
//                                         }else {
//                                             for (DescribeInstancesResponse.Instance.Tag tag : tags){
//                                                 //System.out.println(tag.getTagKey());
//                                                 System.out.println("将tag加入列表");
//                                                 taglist.add(tag.getTagKey());
//                                             }
//                                             while (tagoklist.next()) {
//                                                 System.out.println("asd453f65a186f4we654t???????????");
//                                                 tagok = tagoklist.getString("tag");
//                                                 System.out.println(tagok);
//                                                 if (taglist.contains(tagok)) {
//                                                     busid = tagoklist.getInt("busid");
//                                                     opsuserid = tagoklist.getInt("opsuserid");
//                                                     bususerid = tagoklist.getInt("bususerid");
//                                                     db.updatetagsum(tagok);
//                                                     tagcheck = "true";
//                                                     break;
//                                                 }else {
//                                                     busid = debusid;
//                                                     opsuserid = deopsuserid;
//                                                     bususerid = debususerid;
//                                                 }
//                                             }
//                                             tagoklist.beforeFirst();
//                                             System.out.println(tagok);
//                                             tagstr = "["+String.join(",",taglist)+"]";
//                                             System.out.println(tagstr);
//                                             System.out.println(arn+" bus: "+busid+" opsuser: "+opsuserid+" bususer: "+bususerid);
//                                         }
//                                     }
//                                 }else {
//                                     System.out.println(arn+" bus: "+debusid+" opsuser: "+deopsuserid+" bususer: "+debususerid);
//                                 }
//                             }
                             System.out.println("there is instance in " + region.getRegionId());

                         }


                         System.out.println("instance in " + region.getRegionId() + " is done");
                     }
                     System.out.println( sum);
//                     db.updatenum(sum,slbnum,arn);
                     System.out.println( sum);
                 } catch (ClientException cliente) {
                     cliente.printStackTrace();
                     System.err.println(cliente);
                     System.out.println(arn+"    ClientException:" + cliente);
                 }

                 System.out.println(arn +" done");


             }
             System.out.println("all done");
             try{
                 Long timestamp = System.currentTimeMillis();
                 String yachurl = "https://y345ou.com/robot/send?access_token=V1JXTUqwerqwera3Q2QUssafsdfqwerOE5LQzcwZWdZelRsqrweqwer252dg";
                 String secret = "23542345234";
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
                 mobiles.add("214235125");
                 at.setAtMobiles(mobiles);
                 at.setIsAtAll(false);
                 request.setAt(at);
                 String errmsg = "ecs-sdk-sample:@ewte563 正常运行 @23452364254";
                 System.err.println(errmsg);
                 // 以下是设置各种消息格式的方法
                 sentText(request,errmsg);
                 //    sendLink(request);
                 //    sendMarkdown(request);
                 //    sendActionCard(request);
                 //    sendFeedCard(request);
//                 OapiRobotSendResponse response = dingTalkClient.execute(request);
//                 System.out.println(response.getErrmsg());
             } catch (Exception dinge) {
                 System.out.println("Exception:" + dinge.toString());
             }

         } catch (Exception e){
             try{
                 Long timestamp = System.currentTimeMillis();
                 String yachurl = "https://ya3452ou.com/robot/send?access_token=V1JXTUxkeU1Fawertw3e45ZWdZelRscThQeVNwer3Q0Y2JMS252dg";
                 String secret = "SECfwertwertsdfgserea4d3b5661";
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
                 mobiles.add("34523462345");
                 at.setAtMobiles(mobiles);
                 at.setIsAtAll(false);
                 request.setAt(at);
                 String errmsg = "ecs-sdk-sample:SQLException@sdfg "+e.toString()+" @345346236";
                 System.err.println(errmsg);
                 // 以下是设置各种消息格式的方法
                 sentText(request,errmsg);
                 //    sendLink(request);
                 //    sendMarkdown(request);
                 //    sendActionCard(request);
                 //    sendFeedCard(request);
//                 OapiRobotSendResponse response = dingTalkClient.execute(request);
//                 System.out.println(response.getErrmsg());
             } catch (Exception dinge) {
                 System.out.println("Exception:" + dinge.toString());
             }

         }

//             db.close();

        System.out.println("all done");

    }
}


