package com.ssm.serviceimpl;

import java.util.HashMap;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ssm.dao.UserDao;
import com.ssm.service.UserCount;
@Service
public class UserCountImpl implements UserCount{
	@Autowired
	private UserDao userDao;
	public UserCountImpl() {
		// TODO Auto-generated constructor stub
	}
	//判断登陆，返回的东西有id和mark值
	public HashMap<String, String> ifLog(String id, String password) {
		// TODO Auto-generated method stub
		return userDao.SearchUser(id, password);
	}
	//首先查找是否已经有了这个学生，若是已经有了就不能再注册
	public boolean Regist(String id,String name,
			String password, String password2) {
		if(password!=password2) return false;
		if(userDao.SearchIfExist(id)==true){
			return false;
		}else{
			boolean flag=userDao.AddStu(id, name, password);
			return flag;
		}
	}
	public boolean ChangePassword(String id, String name, 
			String password,String password2) {
		// TODO Auto-generated method stub
		if(password!=password2) return false;
		return userDao.ChangePassword(id, name, password);
	}

}
