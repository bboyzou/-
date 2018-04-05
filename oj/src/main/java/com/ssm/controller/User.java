package com.ssm.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.ssm.serviceimpl.StuCountImpl;
//登陆，注册，忘记密码分发
@Controller
public class User {
	@Autowired
	StuCountImpl stuCountImpl;
	public User() {
	}
	@RequestMapping(value="/log")
    public String Log(@RequestParam("sid") String sid,
    		@RequestParam("password") String password
    		) {
        String mysid=stuCountImpl.ifStulog(sid, password);
        if(mysid!=null){
        	return "success";
        }else {
        	return "fail";
		}
        
    }
	@RequestMapping(value="/regist")
    public String Regist(@RequestParam("username") String username,
    		@RequestParam("password1") String password1,
    		@RequestParam("password1") String password2
    		) {
        
        return "success";
    }
	
}
