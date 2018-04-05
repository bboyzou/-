package com.ssm.dao;

import org.apache.ibatis.annotations.Param;

public interface StudentDao {
	//查找是否有这个账户，登陆的时候用的（根据sid和pawssword）
	String SearchStudent(@Param("sid") String sid,@Param("password") String password);
}
