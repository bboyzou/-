#!/usr/bin/env python
# coding=utf-8
import os
import sys
import subprocess
import logging
import shlex
import config
import lorun
from db import run_sql


result_code = {
    "Waiting": 0,
    "Accepted": 1,
    "Time Limit Exceeded": 2,
    "Memory Limit Exceeded": 3,
    "Wrong Answer": 4,
    "Runtime Error": 5,
    "Output limit": 6,
    "Compile Error": 7,
    "Presentation Error": 8,
    "Unkown Error1": 9,
    "Unkown Error2": 10,
    "System Error": 11,
    "Judging": 12,
}


def run(problem_id, solution_id, language, data_count, user_id, dblock):
    low_level()
    '''获取程序执行时间和内存'''
    #dblock.acquire()
    #time_limit, mem_limit = get_problem_limit(problem_id)
    #dblock.release()
    time_limit = 5 * 1000 #in MS
    mem_limit = 64 * 1024 #in KB
    program_info = {
        "solution_id": solution_id,
        "problem_id": problem_id,
        "take_time": 0,
        "take_memory": 0,
        "user_id": user_id,
        "result": 12,
        "compile_info": "null",
    }
    if check_dangerous_code(solution_id, language) == False:
        program_info['result'] = result_code["Runtime Error"]
        return program_info
    compile_result = compile(solution_id, language, program_info, dblock)
    if compile_result is False:  # 编译错误
        program_info['result'] = result_code["Compile Error"]
        return program_info
    if data_count == 0:  # 没有测试数据
        program_info['result'] = result_code["System Error"]
        return program_info
    result = judge(
        solution_id,
        problem_id,
        data_count,
        time_limit,
        mem_limit,
        program_info,
        result_code,
        language)
    logging.info("Running program over. \n\tThe result is : " + str(result))
    logging.debug(result)
    return result


def check_dangerous_code(solution_id, language):
    if language in ['python2', 'python3']:
        dir_work = os.path.join(config.work_dir, str(solution_id),"main.py")
        code = file(dir_work).readlines()
        support_modules = [
            're',  # 正则表达式
            'sys',  # sys.stdin
            'string',  # 字符串处理
            'scanf',  # 格式化输入
            'math',  # 数学库
            'cmath',  # 复数数学库
            'decimal',  # 数学库，浮点数
            'numbers',  # 抽象基类
            'fractions',  # 有理数
            'random',  # 随机数
            'itertools',  # 迭代函数
            'functools',
            #Higher order functions and operations on callable objects
            'operator',  # 函数操作
            'readline',  # 读文件
            'json',  # 解析json
            'array',  # 数组
            'sets',  # 集合
            'queue',  # 队列
            'types',  # 判断类型
        ]
        for line in code:
            if line.find('import') >= 0:
                words = line.split()
                tag = 0
                for w in words:
                    if w in support_modules:
                        tag = 1
                        break
                if tag == 0:
                    return False
        return True
    if language in ['gcc', 'g++']:
        try:
            dir_work = os.path.join(config.work_dir, str(solution_id),"main.c")
            code = file(dir_work).read()
        except:
            dir_work = os.path.join(config.work_dir, str(solution_id),"main.cpp")
            code = file(dir_work).read()
        if code.find('system') >= 0:
            return False
        return True
    if language == 'java':
        dir_work = os.path.join(config.work_dir, str(solution_id),"Main.java")
        code = file(dir_work).read()
        if code.find('Runtime.')>=0:
            return False
        return True
    if language == 'go':
        dir_work = os.path.join(config.work_dir, str(solution_id),"main.go")
        code = file(dir_work).read()       
        danger_package = [
            'os', 'path', 'net', 'sql', 'syslog', 'http', 'mail', 'rpc', 'smtp', 'exec', 'user',
        ]
        for item in danger_package:
            if code.find('"%s"' % item) >= 0:
                return False
        return True


def compile(solution_id, language, program_info, dblock):
    low_level()
    '''将程序编译成可执行文件'''
    language = language.lower()
    language_to_cmd={
        "c": "gcc",
        "c++": "g++",
        "python": "python2",
    }
    if language in language_to_cmd.keys():
        language = language_to_cmd[language]
    dir_work = os.path.join(config.work_dir, str(solution_id))
    build_cmd = {
        "gcc":
        "gcc main.c -o main",
        #"gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE",
        "g++": 
        #"g++ main.cpp -O2 -Wall -lm --static -DONLINE_JUDGE -o main",
        "g++ main.cpp -o main",
        "java": "javac Main.java",
        "ruby": "reek main.rb",
        "perl": "perl -c main.pl",
        "pascal": 'fpc main.pas -O2 -Co -Ct -Ci',
        "go": '/opt/golang/bin/go build -ldflags "-s -w"  main.go',
        "lua": 'luac -o main main.lua',
        "python2": 'python2 -m py_compile main.py',
        "python3": 'python3 -m py_compile main.py',
        "haskell": "ghc -o main main.hs",
    }
    if language not in build_cmd.keys():
        return False
    p = subprocess.Popen(
        build_cmd[language],
        shell=True,
        cwd=dir_work,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = p.communicate()  # 获取编译错误信息
    logging.info("complie info (empty means OK): " + out+err)
    err_txt_path = os.path.join(config.work_dir, str(solution_id), 'error.txt')
    f = file(err_txt_path, 'w')
    f.write(err)
    f.write(out)
    f.close()
    if p.returncode == 0:  # 返回值为0,编译成功
        return True
    program_info["compile_info"] = err + out
    #dblock.acquire()
    #update_compile_info(solution_id, err + out)  # 编译失败,更新题目的编译错误信息
    #dblock.release()
    return False


def judge(solution_id, problem_id, data_count, time_limit,
          mem_limit, program_info, result_code, language):
    low_level()
    '''评测编译类型语言'''
    max_mem = 0
    max_time = 0
    if language in ["java", 'python2', 'python3', 'ruby', 'perl']:
        time_limit = time_limit * 2
        mem_limit = mem_limit * 16
    logging.info("Start to run, total "+ str(data_count) + " times")
    for i in range(data_count):
        ret = judge_one_mem_time(
            solution_id,
            problem_id,
            i + 1,
            time_limit + 10,
            mem_limit,
            language)
        logging.info("The result of "+str(i)+" cycle is "+str(ret))
        if ret == False:
            continue
        if ret['result'] == 5:
            program_info['result'] = result_code["Runtime Error"]
            return program_info
        elif ret['result'] == 2:
            program_info['result'] = result_code["Time Limit Exceeded"]
            program_info['take_time'] = time_limit + 10
            return program_info
        elif ret['result'] == 3:
            program_info['result'] = result_code["Memory Limit Exceeded"]
            program_info['take_memory'] = mem_limit
            return program_info
        if max_time < ret["timeused"]:
            max_time = ret['timeused']
        if max_mem < ret['memoryused']:
            max_mem = ret['memoryused']
        result = judge_result(problem_id, solution_id, i + 1)
        if result == False:
            continue
        if result == "Wrong Answer" or result == "Output limit":
            program_info['result'] = result_code[result]
            break
        elif result == 'Presentation Error':
            program_info['result'] = result_code[result]
        elif result == 'Accepted':
            if program_info['result'] != 'Presentation Error':
                program_info['result'] = result_code[result]
        else:
            logging.error("judge did not get result")
    program_info['take_time'] = max_time
    program_info['take_memory'] = max_mem
    return program_info


def judge_one_mem_time(
        solution_id, problem_id, data_num, time_limit, mem_limit, language):
    low_level()
    '''评测一组数据'''
    input_path = os.path.join(
        config.data_dir, str(problem_id), 'data%s.in' %
        data_num)
    try:
        input_data = file(input_path)
    except:
        return False
    output_path = os.path.join(
        config.work_dir, str(solution_id), 'out%s.txt' %
        data_num)
    temp_out_data = file(output_path, 'w')
    if language == 'java':
        cmd = 'java -cp %s Main' % (
            os.path.join(config.work_dir,
                         str(solution_id)))
        main_exe = shlex.split(cmd)
        logging.info(main_exe)
    elif language == 'python2':
        cmd = 'python %s' % (
            os.path.join(config.work_dir,
                         str(solution_id),
                         'main.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'python3':
        cmd = 'python3 %s' % (
            os.path.join(config.work_dir,
                         str(solution_id),
                         '__pycache__/main.cpython-33.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'lua':
        cmd = "lua %s" % (
            os.path.join(config.work_dir,
                         str(solution_id),
                         "main"))
        main_exe = shlex.split(cmd)
    elif language == "ruby":
        cmd = "ruby %s" % (
            os.path.join(config.work_dir,
                         str(solution_id),
                         "main.rb"))
        main_exe = shlex.split(cmd)
    elif language == "perl":
        cmd = "perl %s" % (
            os.path.join(config.work_dir,
                         str(solution_id),
                         "main.pl"))
        main_exe = shlex.split(cmd)
    else:
        main_exe = [os.path.join(config.work_dir, str(solution_id), 'main'), ]
    runcfg = {
        'args': main_exe,
        'fd_in': input_data.fileno(),
        'fd_out': temp_out_data.fileno(),
        'timelimit': time_limit,  # in MS
        'memorylimit': mem_limit,  # in KB
    }
    low_level()
    rst = lorun.run(runcfg)
    logging.info("the lorun result is : "+str(rst))
    input_data.close()
    temp_out_data.close()
    logging.debug(rst)
    return rst


def judge_result(problem_id, solution_id, data_num):
    low_level()
    '''对输出数据进行评测'''
    logging.debug("Judging result")
    correct_result = os.path.join(
        config.data_dir, str(problem_id), 'data%s.out' %
        data_num)
    user_result = os.path.join(
        config.work_dir, str(solution_id), 'out%s.txt' %
        data_num)
    try:
        correct = file(
            correct_result).read(
            ).replace(
                '\r',
                '').rstrip(
                )  # 删除\r,删除行末的空格和换行
        user = file(user_result).read().replace('\r', '').rstrip()
    except:
        return False
    if correct == user:  # 完全相同:AC
        return "Accepted"
    if correct.split() == user.split():  # 除去空格,tab,换行相同:PE
        return "Presentation Error"
    if correct in user:  # 输出多了
        return "Output limit"
    return "Wrong Answer"  # 其他WA


def low_level():
    try:
        os.setuid(int(os.popen("id -u %s" % "nobody").read()))
    except:
        pass
try:
    # 降低程序运行权限，防止恶意代码
    os.setuid(int(os.popen("id -u %s" % "nobody").read()))
except:
    logging.error("please run this program as root!")
    sys.exit(-1)
