#!/usr/bin/python
#! -*- coding: utf8 -*-

import lorun
import os

RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

build_cmd = {  
	"gcc"    : "gcc main.c -o main",  
	"g++"    : "g++ main.cpp -o main",  
	"java"   : "javac -J-Xms32m -J-Xmx64m -encoding UTF-8 Main.java",  
	"ruby"   : "ruby -c main.rb",  
	"perl"   : "perl -c main.pl",  
	"pascal" : 'fpc main.pas -O2 -Co -Ct -Ci',  
	"go"     : '/opt/golang/bin/go build -ldflags "-s -w"  main.go',  
	"lua"    : 'luac -o main main.lua',  
	"python2": 'python2 -m py_compile main.py',  
	"python3": 'python3 -m py_compile main.py',  
	"haskell": "ghc -o main main.hs",  
}

run_cmd = {  
	"gcc"    : "./main",  
	"g++"    : "./main",  
	"java"   : "java Main",  
	"ruby"   : "ruby -c main.rb",  
	"perl"   : "perl -c main.pl",  
	"pascal" : 'fpc main.pas -O2 -Co -Ct -Ci',  
	"go"     : '/opt/golang/bin/go build -ldflags "-s -w"  main.go',  
	"lua"    : 'luac -o main main.lua',  
	"python2": 'python2 main.py',  
	"python3": 'python3 main.py',  
	"haskell": "ghc -o main main.hs",  
}

def compileSrc(language):
	if build_cmd.has_key(language):
		if os.system(build_cmd[language]) != 0:
			print('compile failure!')
			return False
    	return True
	return False

def runone(language, in_path, out_path):
    fin = open(in_path)
    ftemp = open('temp.out', 'w')
    
    runcfg = {
        'args':run_cmd[language].split(),
        'fd_in':fin.fileno(),
        'fd_out':ftemp.fileno(),
        'timelimit':10000, #in MS
        'memorylimit':1024*1024, #in KB
    }
    
    rst = lorun.run(runcfg)
    fin.close()
    ftemp.close()
    
    if rst['result'] == 0:
        ftemp = open('temp.out')
        fout = open(out_path)
        crst = lorun.check(fout.fileno(), ftemp.fileno())
        fout.close()
        ftemp.close()
        os.remove('temp.out')
        if crst != 0:
            return {'result':crst}
    
    return rst

def judge(language, td_path, td_total):
    if not compileSrc(language):
        return
    for i in range(td_total):
        in_path = os.path.join(td_path, '%d.in'%i)
        out_path = os.path.join(td_path, '%d.out'%i)
        if os.path.isfile(in_path) and os.path.isfile(out_path):
            rst = runone(language, in_path, out_path)
            rst['result'] = RESULT_STR[rst['result']]
            print(rst)
        else:
            print('testdata:%d incompleted' % i)
            os.remove('./main')
            exit(-1)
    #os.remove('Main.class')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage:%s language testdata_total')
        exit(-1)
    judge(sys.argv[1], "testdata", int(sys.argv[2]))
