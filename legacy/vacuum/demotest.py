import subprocess
import time

# 指定.sh文件的路径
sh_file_path = 'VacuumOnscript.sh'
# sh_file_path = 'VacuumOffscript.sh'

# 使用subprocess.run来执行.sh文件
result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)

# 输出执行结果
print("Standard Output:", result.stdout)
print("Standard Error:", result.stderr)
print("Return Code:", result.returncode)

print("helloworld")

time.sleep(10)


sh_file_path = 'VacuumOffscript.sh'
result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)
