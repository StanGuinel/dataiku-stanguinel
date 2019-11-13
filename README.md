# dataiku-challenge

## Description
Web interface to upload a <i>empire.json</i> file containing the data intercepted by the rebels about the plans of the Empire and to then display the odds (as a percentage) that the Millenium Falcon reaches Endor in time and saves the galaxy and the route to take.

The route is computed using a modified version of Dijkstra's algorithm where nodes are tuples of planet, day and fuel left and are dynamically added to the set of node to visit. At each iteration of the algorithm, the node with the lowest capture probability is visited. For time efficiency, this node is retrieved using a min-heap.

The most important function is the <i>odds()</i> functions in the <i>utils.py</i> file that does all the route and odds computation.

## Setup
``` 
git clone git@github.com:StanGuinel/dataiku-challenge.git
cd dataiku-challenge
pip install -r requirements.txt
python run.py
```

## How to use
- Visit http://127.0.0.1:5000/upload
- Upload the empire.json file
- See the probability of success and the route to take if there is one.

