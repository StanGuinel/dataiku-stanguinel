from utils import *
import argparse

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="Empire JSON file", required=True)
	args = parser.parse_args()

	empire_file = args.file

	rebel_file = "millenium-falcon.json"

	route_description, captured_proba, total_day = odds(rebel_file, empire_file)

	print("Probability of success is %s%% in %s days\n" % (int((1-captured_proba)*100),total_day))
	for step in route_description:
		print(step)


