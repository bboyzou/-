package com.ssm.serviceimpl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ssm.dao.StudentDao;
import com.ssm.service.StuCount;
@Service
public class StuCountImpl implements StuCount{
	@Autowired
	private StudentDao studentDao;
	public StuCountImpl() {
		// TODO Auto-generated constructor stub
	}

	public String ifStulog(String sid, String password) {
		return studentDao.SearchStudent(sid, password);
	}

	public String ifExistINstudent(String sid) {
		// TODO Auto-generated method stub
		return null;
	}

	public String TeacherRegist(String tid, String password1, String password2) {
		// TODO Auto-generated method stub
		return null;
	}

}
