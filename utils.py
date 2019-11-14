import json
import pandas as pd
import sqlite3
import heapq
import numpy as np

class State:
	'''
	a state is a tuple of planet, day and fuel left
	'''
	def __init__(self, planet, day, fuel):
		self.planet = planet
		self.day = day
		self.fuel = fuel

	def __lt__(self, other):
         return self.day < other.day

class BountyHunters:
	'''
	a class to record in a set the list of planets and days where the bounty hunters will be
	'''
	def __init__(self, bounty_hunters):
		hunters = set()
		for x in bounty_hunters:
			hunters.add((x["planet"], x["day"]))
		# set of (planet, day) with bounty hunters
		self.hunters = hunters

	def huntersHere(self, state):
		# return True if bounty hunters are in this state (same planet and same day)
		return (state.planet, state.day) in self.hunters

class Travel:
	'''
	class that represent the mission to do and with function to compute the best route
	'''
	def __init__(self, rebel, empire, universe):
		self.autonomy = rebel["autonomy"]
		self.departure = rebel["departure"]
		self.arrival = rebel["arrival"]
		self.countdown = empire["countdown"]
		self.hunters = BountyHunters(empire["bounty_hunters"])
		self.adjacency = adjacencyList(universe)

	def possibleNeighbors(self, state):
		'''
		return a list of neighbors states that are possible
		'''
		neighbors = []
		if state.planet != self.arrival:
			refuel_stop = False
			for planet, travel_time in self.adjacency[state.planet]:
				cntdwn = self.countdown if planet == self.arrival else self.countdown-1
				
				if state.day + travel_time <= cntdwn and state.fuel >= travel_time:
					neighbors += [State(planet, state.day+travel_time, state.fuel-travel_time)]

				if state.day + travel_time < cntdwn:	# is a refuel/waiting day possible
					refuel_stop = True

			if refuel_stop:	# refuel even when just waiting
				neighbors += [State(state.planet, state.day+1, self.autonomy)]

		return neighbors


	def bestRoute(self):
		'''
		return the best route and the probability of being captured
		'''
		ToDo = set()	# set of state to process
		Done = set()	# set of states already processed
		start = State(self.departure, 0, self.autonomy)		# first state
		ToDo.add(start)
		state_nb = 1	# dynamic number of total states to explore

		capture = {}	# dictionary of number of possible captures of each state
		capture[start] = 1 if self.hunters.huntersHere(start) else 0

		ToDo_heap = [(capture[start], start)]
		heapq.heapify(ToDo_heap)	# min-heap to get state with min capture value faster

		prev = {}	# dictionary to save from which state we arrived to this state

		failure = True

		while len(Done) < state_nb:
			# state with min capture value in ToDo but not in Done
			current_state = heapq.heappop(ToDo_heap)[1]
			# current_state = min(ToDo, key=lambda state: capture[state])	# without min-heap

			if current_state not in Done:	# can already be in Done if it was pushed multiple time with different capture value in the min-heap
				Done.add(current_state)
				ToDo.remove(current_state)

				for neighbor in self.possibleNeighbors(current_state):
					if neighbor not in Done:
						k = 1 if self.hunters.huntersHere(neighbor) else 0	# are there hunters in neighbor

						if neighbor.planet == self.arrival: # a possible neighbor is the arrival (i.e. no failure)
							failure = False

						if neighbor not in capture:	# give "infinite" capture value to unseen neighbor
							capture[neighbor] = 1000

						updated = False
						if capture[current_state] + k < capture[neighbor]:	# update capture value
							capture[neighbor] = capture[current_state] + k
							prev[neighbor] = current_state
							updated = True

						if neighbor not in ToDo:
							ToDo.add(neighbor)
							heapq.heappush(ToDo_heap, (capture[neighbor], neighbor))
							state_nb += 1
						else:
							if updated:	# update ToDo_heap with the new capture value (necessary lower value) of neighbor
								heapq.heappush(ToDo_heap, (capture[neighbor], neighbor))

		if failure:	# arrival was not reached
			return [], 1
		
		# find the state with arrival planet that has minimum capture value
		min_state = min(capture, key=lambda state: capture[state] if state.planet==self.arrival else 1000)

		# retrieve route from arrival to departure using the prev dictionary
		route = []
		state = min_state
		while state in prev:
			route.insert(0, (state,capture[state]))
			state = prev[state]
		route.insert(0, (state,capture[state]))

		return route, oddsComputation(capture[min_state])

def adjacencyList(universe):
	'''
	return an adjacency list from the universe dataframe
	'''
	adjacency = {}
	for index, row in universe.iterrows():
		if row["origin"] in adjacency:
			adjacency[row["origin"]] += [(row["destination"],row["travel_time"])]
		else:
			adjacency[row["origin"]] = [(row["destination"],row["travel_time"])]

		if row["destination"] in adjacency:
			adjacency[row["destination"]] += [(row["origin"],row["travel_time"])]
		else:
			adjacency[row["destination"]] = [(row["origin"],row["travel_time"])]

	return adjacency

def readFiles(rebel_file, empire_file):
	'''
	read json files and database and convert them into dictionaries and dataframe
	'''
	with open(rebel_file) as json_file:
		rebel = json.load(json_file)

	with open(empire_file) as json_file:
		empire = json.load(json_file)

	cnx = sqlite3.connect(rebel["routes_db"])
	universe = pd.read_sql_query("SELECT * FROM ROUTES", cnx)	

	if universe.isnull().sum().sum() > 0:
		raise ValueError("Universe database has missing values")
	elif not np.array_equal(np.array(universe.columns), np.array(['origin', 'destination', 'travel_time'])):
		raise ValueError("Universe database has wrong column names (expected ['origin', 'destination', 'travel_time'])")
	elif not universe['travel_time'].min() > 0:
		raise ValueError("Universe database has none striclty positive travel time")

	return rebel, empire, universe

def odds(rebel_file, empire_file):
	'''
	return the odds (as a percentage) that the Millenium Falcon reaches Endor in time and saves the galaxy.
 	'''
	rebel, empire, universe = readFiles(rebel_file, empire_file)
	travel = Travel(rebel, empire, universe)
	best_route, captured_proba = travel.bestRoute()

	route_description, total_day = routeDescription(best_route)

	return route_description, captured_proba, total_day

def oddsComputation(k):
	'''
	compute the total probability of being captured where k is the number of times the Bounty Hunter tried to capture the Millenium Falcon
	'''
	return sum([(9**i)/(10**(i+1)) for i in range(k)])

def routeDescription(route):
	'''
	return a string that describes the route to take from a list of states and the number of days
	'''
	if len(route) <= 1:
		return ["You cannot save the galaxy, failure of the mission is inevitable !"], 0
	else:
		route_description = []
		for i in range(len(route)-1):
			prev, curr = route[i], route[i+1]
			suffix = ""
			if prev[1] < curr[1]:
				suffix += ", with 10% chance of being captured on day " +  str(curr[0].day) + " on " + curr[0].planet

			if prev[0].planet == curr[0].planet:
				if prev[0].fuel < curr[0].fuel:
					route_description += ["Refuel on " + curr[0].planet + suffix]
				else:
					route_description += ["Wait 1 day on " + curr[0].planet + suffix]
			else:
				route_description += ["Travel from " + prev[0].planet + " to " + curr[0].planet + suffix]
		
		return route_description, route[-1][0].day


