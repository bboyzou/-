package com.ssm.service;
//学生登陆注册所用
public interface StuCount {
	// 根据学生的账号密码查询是否有这个人，登陆的时候所用的
	public String ifStulog(String sid, String password);

	// 不允许重复注册
	public String ifExistINstudent(String sid);

	// 注册
	public String TeacherRegist(String tid, String password1, String password2);
}
