<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>测试SpringMVC</title>
</head>
<body>
	<form action="log" method="POST">
		<table>
			<tr>
				<td><label>账号:</label></td>
				<td><input type="text" required="required" id="id"
					name="id"></input></td>
			</tr>
			<tr>
				<td><label>密码:</label></td>
				<td><input type="text" required="required" id="password"
					name="password"></input></td>
			</tr>
			<tr>
				<td><input id="submit" type="submit" value="确认注册？"></td>
			</tr>
		</table>
	</form>
</body>
</html>