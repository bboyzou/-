package com.ssm.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.ssm.serviceimpl.UserCountImpl;
//登陆，注册，忘记密码分发
@Controller
public class User {
	@Autowired
	private UserCountImpl userCountImpl;
	public User() {
	}
	@RequestMapping(value="/log")
    public String Log(@RequestParam("id") String id,
    		@RequestParam("password") String password
    		) {
		Map<String, String> map=new HashMap<String, String>();
		map=userCountImpl.ifLog(id, password);
        String myid=map.get("id");
        if(myid!=null){
        	return "success";
        }else {
        	return "fail";
		}
        
    }
	@RequestMapping(value="/regist")
    public String Regist(@RequestParam("id") String id,
    		@RequestParam("name") String name,
    		@RequestParam("password") String password,
    		@RequestParam("password2") String password2
    		) {
        boolean flag=userCountImpl.Regist(id, name,password, password2);
        if(flag) return "success";
        else{
        	return "fail";
        }
    }
	@RequestMapping(value="/changepassword")
    public String ChangePassword(@RequestParam("id") String id,
    		@RequestParam("name") String name,
    		@RequestParam("password") String password,
    		@RequestParam("password2") String password2
    		) {
        boolean flag=userCountImpl.ChangePassword(id, name, password,password2);
        if(flag) return "success";
        else{
        	return "fail";
        }
    }
	
}
