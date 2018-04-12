#!/usr/bin/env python
# coding=utf-8
"""
为了服务器安全，隐藏部分sql语句。
程序执行需要相关数据库和测试数据。
"""
import os
import sys
import codecs
import logging
import shutil
import time
import config
import threading
from datetime import datetime
from db import run_sql, run_sql_without_return
from Queue import Queue
from run_program import run

code_result=[
    "Waiting",
    "Accepted",
    "Time Limit Exceeded",
    "Memory Limit Exceeded",
    "Wrong Answer",
    "Runtime Error",
    "Output limit",
    "Compile Error",
    "Presentation Error",
    "Unkown Error1"
    "Unkown Error2"
    "System Error",
    "Judging",  
]


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

# 初始化队列
q = Queue(config.queue_size)
# 创建数据库锁，保证一个时间只能一个程序都写数据库
dblock = threading.Lock()


def start_work_thread():
    '''开启工作线程'''
    for i in range(config.count_thread):
        t = threading.Thread(target=worker)
        t.deamon = True
        t.start()


def start_get_task():
    '''开启获取任务线程'''
    t = threading.Thread(target=put_task_into_queue, name="get_task")
    t.deamon = True
    t.start()


def worker():
    '''工作线程，循环扫描队列，获得评判任务并执行'''
    while True:
        if q.empty() is True:  # 队列为空，空闲
            logging.info("%s idle" % (threading.current_thread().name))
        task = q.get()  # 获取任务，如果队列为空则阻塞
        solution_id = task['solution_id']
        problem_id = task['problem_id']
        language = task['language']
        user_id = task['user_id']
        data_count = get_data_count(task['problem_id'])  # 获取测试数据的个数
        logging.info("judging %s" % solution_id)
        result = run(
            problem_id,
            solution_id,
            language,
            data_count,
            user_id,
            dblock)  # 评判
        logging.info(
            "%s result %s" % (
                result[
                    'solution_id'],
                result[
                    'result']))
        dblock.acquire()
        update_result(task,result)  # 将结果写入数据库
        dblock.release()
        if config.auto_clean:  # 清理work目录
            clean_work_dir(result['solution_id'])
        q.task_done()  # 一个任务完成

#需要将数据库的测试数据写入到预定的文件里去

def get_data_count(problem_id):
    '''获得测试数据的个数信息'''
    full_path = os.path.join(config.data_dir, str(problem_id))#合并目录，如good+text合并成good/text
    try:
        files = os.listdir(full_path)#listdir()方法返回一个列表，其中包含由path指定的目录中的条目的名称
    except OSError as e:
        logging.error(e)
        return 0
    count = 0
    for item in files:
        if item.endswith(".in") and item.startswith("data"):
            count += 1
    return count


def clean_work_dir(solution_id):
    '''清理word目录，删除临时文件'''
    dir_name = os.path.join(config.work_dir, str(solution_id))
    print(dir_name)
    shutil.rmtree(dir_name)


def put_task_into_queue():
    '''循环扫描数据库,将任务添加到队列'''
    while True:
        q.join()  # 阻塞程序,直到队列里面的任务全部完成
        # 删除时间超过 1天 的数据。
        delete_sql = "delete from judgeOL_submitcode where `submit_date` < date_sub(now(), interval 1 day)"
        run_sql(delete_sql)
        # 找出所有等待处理的数据
        sql = "select id,language,submit_code_text,problem_id,user_id from judgeOL_submitcode " \
              "where status='Waiting' order by submit_date DESC"
        # 返回数据库类型的数据
        data = run_sql(sql)
        time.sleep(0.2)  # 延时0.2秒,防止因速度太快不能获取代码
        for i in data:
            solution_id, language, submit_code_text, problem_id, user_id = i
            logging.info("The language is : "+ language)
            dblock.acquire()
            ret = get_code(solution_id, problem_id, language)
            dblock.release()
            if ret == False:
                # 防止因速度太快不能获取代码
                time.sleep(0.5)
                dblock.acquire()
                ret = get_code(solution_id, problem_id, language)
                logging.info("The SECOND get the code is"+str(ret))
                dblock.release()
            if ret == False:
                dblock.acquire()
                logging.info("The THIRD failure!")		
                update_solution_status(solution_id, "System Error")
                dblock.release()
                # 清理暂时进行代码处理的文件夹
                clean_work_dir(solution_id)
                continue
            task = {
                "solution_id": solution_id,
                "problem_id": problem_id,
                "submit_code_text": submit_code_text,
                "user_id": user_id,
                "language": language,
            }
            q.put(task)
            dblock.acquire()
            update_solution_status(solution_id, "Judging")
            dblock.release()
        time.sleep(0.5)


def update_solution_status(solution_id, condition):
    sql = "update judgeOL_submitcode set status='" + condition + "' where id=" + str(solution_id)
    run_sql(sql)


def update_result(task, result):
    id_result = result['result']
    condition = code_result[id_result]
    sql = "update judgeOL_submitcode set status='" + condition + "' where id=" + str(task['solution_id'])
    run_sql(sql)
    if condition == "Accepted":
        dt = datetime.now()
        max_time = result['take_time']
        max_mem = result['take_memory']
        time_now = dt.strftime('%Y-%m-%d %H:%M:%S')
        sql = "insert into judgeOL_acceptedcode(accepted_code_text,language," \
              "accepted_date,time_cost, memory_cost,problem_id,user_id) " \
              "values('" + task['submit_code_text'] + "','" + task['language'] + "','" + \
              time_now + "'," + str(max_time) + "," + str(max_mem) + "," + \
              str(task['problem_id']) + "," + str(task['user_id']) + ")"
        run_sql_without_return(sql)
    if condition == "Compile Error":
        sql = "update judgeOL_submitcode set compile_info = '" + result["compile_info"] + "' where id=" + str(task['solution_id'])
        run_sql_without_return(sql)

#可以在此处获取测试数据写如测试数据的目录下，与get_code类似的写法
def data_split(test_work,num,testdata):
    test_data=testdata.split("#")
    file_name_in="data%s.in" %num
    file_name_out="data%s.out" %num
    real_path_in=os.path.join(
            test_work,
            file_name_in)
    real_path_out=os.path.join(
            test_work,
            file_name_out)
    try:
        #low_level()
        f_in = codecs.open(real_path_in, 'w')
        f_out = codecs.open(real_path_out, 'w')
        try:
            f_in.write(test_data[0])
            f_out.write(test_data[1])
        except:
            logging.info(" not write testdata to file" )
            f_in.close()
            f_out.close()
            return False
        f_in.close()
        f_out.close()
    except OSError as e:
        logging.info(e)
        return False
        
def get_testdata(problem_id):
    ''' 从数据库读取测试数据写入文本中'''
    select_testdata_sql="select data from testdate where problem_id = "+str(problem_id)
    feh = run_sql(select_testdata_sql)
    
    try:
        test_work=os.path.join(config.data_dir, str(problem_id))
        os.mkdir(test_work)#os.mkdir() 方法用于以数字权限模式创建目录。默认的模式为 0777 (八进制)。
    except OSError as e:
        if str(e).find("exist") > 0:  # 文件夹已经存在
            pass
        else:
            logging.info(e)
            return False
    if feh is not None:
       a=1
       for row in feh:
          data=row[0]
          data_split(test_work,a,data)
          a=a+1
    else:
        logging.info("1 cannot get testdata  ")
        return False
         
def get_code(solution_id, problem_id, language):
    '''从数据库获取代码并写入work目录下对应的文件'''
    file_name = {
        "c": "main.c",
        "c++": "main.cpp",
        "java": "Main.java",
        'ruby': "main.rb",
        "perl": "main.pl",
        "pascal": "main.pas",
        "go": "main.go",
        "lua": "main.lua",
        'python': 'main.py',
        'python3': 'main.py',
        "haskell": "main.hs"
    }
    select_code_sql = "select submit_code_text from judgeOL_submitcode where id = " + str(solution_id)
    feh = run_sql(select_code_sql)
    if feh is not None:
        try:
            code = feh[0][0]
        except:
            logging.info("1 cannot get code of runid %s" % solution_id)
            return False
    else:
        logging.info("2 cannot get code of runid %s" % solution_id)
        return False
    try:
        work_path = os.path.join(config.work_dir, str(solution_id))
        #low_level()
        os.mkdir(work_path)#os.mkdir() 方法用于以数字权限模式创建目录。默认的模式为 0777 (八进制)。
    except OSError as e:
        if str(e).find("exist") > 0:  # 文件夹已经存在
            pass
        else:
            logging.info(e)
            return False
    try:
        if file_name[language]:
        	logging.info("The language is : "+file_name[language])
        else:
        	logging.info("Wrong language name")
        real_path = os.path.join(
            work_path,
            file_name[language])
    except KeyError as e:
        logging.info(e)
        return False
    try:
        #low_level()
        f = codecs.open(real_path, 'w')
        try:
            f.write(code)
            get_testdata(problem_id)#将测试数据写入文件
        except:
            logging.info("%s not write code to file" % solution_id)
            f.close()
            return False
        f.close()
    except OSError as e:
        logging.info(e)
        return False
    return True



def check_thread():
    #low_level()
    '''检测评测程序是否存在,小于config规定数目则启动新的'''
    while True:
        try:
            if threading.active_count() < config.count_thread + 2:
                logging.info("start new thread")
                t = threading.Thread(target=worker)
                t.deamon = True
                t.start()
            time.sleep(1)
        except:
            pass


def start_protect():
    '''开启守护进程'''
    #low_level()
    t = threading.Thread(target=check_thread, name="check_thread")
    t.deamon = True
    t.start()


def main():
    #low_level()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s --- %(message)s', )
    start_get_task()
    start_work_thread()
    start_protect()


if __name__ == '__main__':
    main()
