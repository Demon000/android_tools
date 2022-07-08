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

	def fill_matched_indices(self, matched_indices):
		matches = []

		for match in self.matches:
			new_match = match.fill_matched_indices(matched_indices)
			matches.append(new_match)

		return Macro(self.name, matches, self.replace_fn)
