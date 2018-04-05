package com.ssm.service;
//老师登陆注册所用
public interface TeaCount {
	//根据教师的账号密码查询是否有这个人，登陆的时候所用的
	public String ifTeacherlog(String tid,String password);
	//注册的时候所用，首先在myteacher表中查询是否有老师的这个账号，这个表的数据由管理院来添加
	//如果有这个账号，到下一步
	public String ifExistINmyteacher(String tid);
	//这个接上一步，如果myteacher表中有这个账号，再接着查找teacher表中是否已经有了，
	//不允许重复注册
	public String ifExistINteacher(String tid);
	//注册
	public String TeacherRegist(String tid,String password1,String password2);
}
