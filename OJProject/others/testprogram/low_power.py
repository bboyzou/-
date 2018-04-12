import os

def low_level():
    try:
        os.setuid(int(os.popen("id -u %s" % "nobody").read()))
    except:
        pass
try:
    os.setuid(int(os.popen("id -u %s" % "nobody").read()))
except:
    print("please run this program as root!")


low_level()
os.system("./main")

