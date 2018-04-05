package com.ssm.service;

import javax.ws.rs.GET;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ssm.dao.StudentDao;
@Service
public class Test {
	@Autowired
	private StudentDao studentDao;
	public Test() {
		
	}
	public String GET(String sid, String password){
		 return studentDao.SearchStudent(sid,password);
		
	}
}
