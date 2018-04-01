package com.ssm.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class Hello {

    @RequestMapping("/regist")
    public String hello(@RequestParam("username") String username,
    		@RequestParam("password1") String password1,
    		@RequestParam("password1") String password2
    		) {
        System.out.println("==============start=============");
        System.out.println("你成功创建了一个springmvc项目");
        System.out.println("==============end=============");
        System.out.println(username);
        System.out.println(password1);
        System.out.println(password2);
        return "success";
    }

}
