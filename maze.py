import sys
from abc import ABC, abstractmethod

# Node Class to hold state parent and possible actions

class Node():
	def __init__(self, state, parent, action):
		self.state = state
		self.parent = parent
		self.action = action

# AFrontier is a abstract base class for StackFrontier and QueueFrontier classes

class AFrontier(ABC):
	def __init__(self):
		self.frontier = []
	def push(self, node):
		self.frontier.append(node)
	def empty(self):
		return (len(self.frontier) == 0)
	def contains_state(self, state):
		return any(node.state==state for node in self.frontier)
	@abstractmethod
	def pop(self):
		pass

# StackFrontier Class which will be used for depth-first-search	

class StackFrontier(AFrontier):
	def pop(self):
		if len(self.frontier) == 0:
			raise Exception("Empty frontier")
		node = self.frontier[-1]
		del self.frontier[-1]
		return node

# QueueFrontier Class which will be used for breath-first-search	

class QueueFrontier(AFrontier):
	def pop(self):
		if len(self.frontier) == 0:
			raise Exception("Empty frontier")
		node = self.frontier[0]
		del self.frontier[0]
		return node

# Maze Class which will have all necessary information of the maze

class Maze():
	# Parse file
	def __init__(self, filename):
		with open(filename) as f:
			content = f.read()
		
		if content.count('A') != 1:
			raise Exception("Maze must have only one starting position")
		if content.count('B') != 1:
			raise Exception("Maze must have only one exit")

		content = content.splitlines()
		self.height = len(content)
		self.width = max(len(line) for line in content)

		self.walls = []
		for i in range(self.height):
			row = []
			for j in range(self.width):
				try:
					if content[i][j] == "A":
						self.start = (i, j)
						row.append(False)
					elif content[i][j] == "B":
						self.goal = (i, j)
						row.append(False)
					elif content[i][j] == " ":
						row.append(False)
					elif content[i][j] == "#":
						row.append(True)
					else:
						raise Exception("invalid character in map: " + content[i][j] + ": line: " + str(i + 1))
				except IndexError:
					row.append(False)
			self.walls.append(row)

		self.solution = None
	
	def __str__(self):
		solution = self.solution[1] if self.solution is not None else None
		s = "\n"
		for i, row in enumerate(self.walls):
			for j, col in enumerate(row):
				if col:
					s += "█"
				elif (i, j) == self.start:
					s += "A"
				elif (i, j) == self.goal:
					s += "B"
				elif solution is not None and (i, j) in solution:
					s += "*"
				else:
					s += " "
			s += "\n"
		return s
	
	# Print all actions needed to solve maze
	def print_actions(self):
		solution = self.solution[0]
		for i in range(len(solution) - 1):
			if solution[i] != solution[i + 1]:
				print(solution[i])
		print(solution[-1])

	# Returns all possible states from a specific state
	def neighbors(self, state):
		row, col = state
		candidates = [
			("up", (row - 1, col)),
			("down", (row + 1, col)),
			("right", (row, col + 1)),
			("left", (row, col - 1)),
		]

		res = []
		for action, (r, c) in candidates:
			if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
				res.append(((action), (r, c)))
		return res

	def solve(self, search_algo):
		# Set initial state
		initial_node = Node(state=self.start, parent=None, action=None)
		
		if search_algo == "DFS":
			frontierObj = StackFrontier
		elif search_algo == "BFS":
			frontierObj = QueueFrontier
		else:
			raise Exception("Choose a valid search algoritm (DFS / BFS)")
		frontier = frontierObj()
		frontier.push(initial_node)

		# Set explored set and number of explored nodes
		self.explored = set()
		self.nb_explored = 0

		while True:
			# Check if frontier empty then no solution
			if frontier.empty():
				raise Exception("No solution!")
			# Pop node from the frontier to consider
			node = frontier.pop()
			self.nb_explored += 1
			# If node is goal node return solution
			if node.state == self.goal:
				actions = []
				cells = []
				while node.parent is not None:
					actions.append(node.action)
					cells.append(node.parent.state)
					node = node.parent
				actions.reverse()
				cells.reverse()
				self.solution = (actions, cells)
				return
			# Add state to explored sets
			self.explored.add(node.state)
			# Expand node if not in frontier and not already explored
			for action, state in self.neighbors(node.state):
				if not frontier.contains_state(state) and state not in self.explored:
					frontier.push(Node(state=state, parent=node, action=action))
	# Output result image using pillow
	def output_image(self, filename, show_solution=True, show_explored=False):
		from PIL import Image, ImageDraw
		cell_size = 50
		cell_border = 2

		img = Image.new(
			"RGBA",
			(self.width * cell_size, self.height * cell_size),
			"black"
		)
		draw = ImageDraw.Draw(img)

		solution = self.solution[1] if self.solution is not None else None
		for i, row in enumerate(self.walls):
			for j, col in enumerate(row):
				if col:
					fill = (40, 40, 40)
				elif (i, j) == self.start:
					fill = (255, 0, 0)
				elif (i, j) == self.goal:
					fill = (0, 171, 28)
				elif solution is not None and show_solution and (i, j) in solution:
					fill = (220, 235, 113)
				elif solution is not None and show_explored and (i, j) in self.explored:
					fill = (212, 97, 85)
				else:
					fill = (237, 240, 252)
				draw.rectangle(
					([(j * cell_size + cell_border, i * cell_size + cell_border),
					((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
					fill=fill
				)
		img.save(filename)

if len(sys.argv) != 2 and len(sys.argv) != 3:
	sys.exit("Usage: python maze.py maze.txt (DFS / BFS)")

maze = Maze(sys.argv[1])
print("Maze: \n", maze)
print("Solving maze ...")
try:
	maze.solve(sys.argv[2])
except IndexError:
	maze.solve("BFS")
print("States Explored: ", maze.nb_explored)
print("Solution:")
print(maze)
print("Actions: ")
maze.print_actions()
maze.output_image("maze.png", show_explored=True)