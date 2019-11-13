from utils import *
import time


rebel_file = "millenium-falcon.json"
empire_file = "empire.json"

route_description, captured_proba, total_day = odds(rebel_file, empire_file)

print("Probability of success is %s%% in %s days\n" % (int((1-captured_proba)*100),total_day))
for step in route_description:
	print(step)


