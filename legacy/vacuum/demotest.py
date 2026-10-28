import subprocess
import time

# Specify the shell script path.
sh_file_path = 'VacuumOnscript.sh'
# sh_file_path = 'VacuumOffscript.sh'

# Execute the shell script with subprocess.run.
result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)

# Print the execution result.
print("Standard Output:", result.stdout)
print("Standard Error:", result.stderr)
print("Return Code:", result.returncode)

print("helloworld")

time.sleep(10)


sh_file_path = 'VacuumOffscript.sh'
result = subprocess.run(['bash', sh_file_path], capture_output=True, text=True)
