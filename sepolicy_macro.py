class Macro:
	def __init__(self, name, matches, replace_fn=None):
		self.name = name
		if not isinstance(matches, list):
			matches = [matches]
		self.matches = matches
		self.replace_fn = replace_fn
		self.max_index = None

		for match in matches:
			if match.max_index is not None and \
				(self.max_index is None or \
					match.max_index > self.max_index):
				self.max_index = match.max_index

	def __str__(self):
		s = ''
		s += f'Macro:\n'
		s += f'name: {self.name}\n'
		s += f'is_fully_filled: {self.is_fully_filled()}\n'
		s += f'matches:\n'
		for match in self.matches:
			s += str(match)
		return s

	def fill_matched_indices(self, matched_indices):
		matches = []

		for match in self.matches:
			new_match = match.fill_matched_indices(matched_indices)
			matches.append(new_match)

		return Macro(self.name, matches, self.replace_fn)
