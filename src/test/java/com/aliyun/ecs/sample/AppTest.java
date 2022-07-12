package com.aliyun.ecs.sample;

import java.io.IOException;
import java.sql.ResultSet;

public class AppTest {
    public static void main(String[] args) throws IOException {

        try {
        mysql db = new mysql();

        ResultSet arnlist = db.getarn();
        ResultSet tagoklist = db.gettags();

            while (arnlist.next()) {
                String arn = arnlist.getString("arn");
                int busid = arnlist.getInt("business_ids");
                int opsuerid = arnlist.getInt("opsuserid");
                int busuerid = arnlist.getInt("bususerid");
                System.out.println(arn+" bus: "+busid+" opsuser: "+opsuerid+" bususer: "+busuerid);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }



    }
}
