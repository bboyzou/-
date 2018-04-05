//package com.ssm.controller;
//
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.stereotype.Controller;
//import org.springframework.web.bind.annotation.RequestMapping;
//import org.springframework.web.bind.annotation.RequestParam;
//
//import com.ssm.dao.StudentDao;
//import com.ssm.service.Test;
//
//@Controller
//public class Hello {
//	@Autowired
//	Test test;
//	
//    @RequestMapping(value="/log")
//    public String hello(@RequestParam("sid") String sid,
//    		@RequestParam("password") String password
//    		) {
//        System.out.println("==============start=============");
//        System.out.println("你成功创建了一个springmvc项目");
//        System.out.println("==============end=============");
//        System.out.println(sid);
//        System.out.println(password);
//        String a=test.GET(sid, password);
//        System.out.println("我的:"+a);
//        return "success";
//    }
//    @RequestMapping("/r")
//    public String gg(){
//    	System.out.println("==============start=============");
//        System.out.println("你成功创建了一个springmvc项目");
//        System.out.println("==============end=============");
//    	return "success";
//    }
//}
