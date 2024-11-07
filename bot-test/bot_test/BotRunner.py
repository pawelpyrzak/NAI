import subprocess

plik1 = subprocess.Popen(["poetry", "run", "python", "bot_test/dc/dc_bot.py"])
plik2 = subprocess.Popen(["poetry", "run", "python", "bot_test/slack/slackv2.py"])
plik3 = subprocess.Popen(["poetry", "run", "python", "bot_test/telegram/telegram2.py"])

plik1.wait()
plik2.wait()
plik3.wait()