class Macro:
	def __init__(self, name, matches, replace_fn=None):
		self.name = name
		if not isinstance(matches, list):
			matches = [matches]
		self.matches = matches
		self.replace_fn = replace_fn
		self.max_index = -1

		for match in matches:
			if match.max_index is not None and \
				match.max_index > self.max_index:
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

	def is_fully_filled(self):
		return self.max_index == -1

	def fill_matched_indices(self, matched_indices):
		matches = []

		for match in self.matches:
			new_match = match.fill_matched_indices(matched_indices)
			matches.append(new_match)

		return Macro(self.name, matches, self.replace_fn)

class MacroMatchResult:
	def __init__(self, filled_macro, rules, types):
		self.filled_macro = filled_macro
		self.rules = rules
		self.types = types

	def __str__(self):
		s = ''
		s += f'MatchResult:\n'
		s += f'filled_macro: {self.filled_macro}\n'
		s += f'types: {self.types}\n'
		s += f'rules:\n'
		for rule in self.rules:
			s += str(rule) + '\n'
		return s

class MacroReplaceResult:
	def __init__(self, added=[], removed=[]):
		self.added = added
		self.removed = removed

	def __str__(self):
		s = ''
		s += f'ReplaceResult:\n'
		s += f'removed:\n'
		for rule in self.removed:
			s += str(rule) + '\n'
		s += f'added:\n'
		for rule in self.added:
			s += str(rule) + '\n'
		return s
