import re

import parse

def extract_index(part):
	pattern = r'\$(\d+)'
	indices = re.findall(pattern, part)
	l = len(set(indices))

	if l > 1:
		raise Exception('Cannot handle multiple match indices: {indices}')

	if l == 0:
		index = None
	else:
		part = part.replace('{', '{{')
		part = part.replace('}', '}}')
		part = re.sub(pattern, '{0}', part)
		index = int(indices[0]) - 1

	return part, index


class Match:
	def __init__(self, parts=None, parts_contains=None, contains=None, equal=None):
		self.match_indices = []
		self.max_index = -1
		self.contains = None
		self.equal = None
		self.parts = None
		self.parts_len = None
		self.parts_contains = None

		if contains is not None:
			self.contains = set(contains)
		elif equal is not None:
			self.equal = set(equal)

		if parts is not None:
			self.parts_len = len(parts)
			self.parts = []

			for i in range(self.parts_len):
				part = parts[i]
				part, index = extract_index(part)

				if index is not None and index > self.max_index:
					self.max_index = index

				self.match_indices.append(index)
				self.parts.append(part)
		elif parts_contains is not None:
			self.parts_contains = parts_contains

	def __str__(self):
		s = ''
		s += f'Match:\n'
		s += f'is_fully_filled: {self.is_fully_filled()}\n'
		s += f'parts: {self.parts}\n'
		s += f'parts_contains: {self.parts_contains}\n'
		s += f'contains: {self.contains}\n'
		s += f'equal: {self.equal}\n'
		return s

	def is_fully_filled(self):
		return self.max_index == -1

	def parse_match(self, match_part, rule_part):
		result = parse.parse(match_part, rule_part)
		if result is None:
			return None

		return result[0]

	def match_part_index(self, rule_part, i):
		if self.parts_contains is not None:
			return True

		if i >= self.parts_len:
			return True

		match_part = self.parts[i]

		if self.match_indices[i] is not None:
			result = self.parse_match(match_part, rule_part)
			return result is not None
		elif match_part == rule_part:
			return True

		return False

	def match_rule_parts_contains(self, rule):
		if self.parts_contains is None:
			return True

		for rule_part in rule.parts:
			if rule_part in self.parts_contains:
				return True

		return False

	def match_rule_varargs(self, rule):
		if self.equal is not None:
			return self.equal == rule.varargs

		if self.contains is not None:
			return self.contains.issubset(rule.varargs)

		return True

	def extract_matched_indices(self, rule):
		assert self.parts is not None

		matched_indices = [None] * (self.max_index + 1)
		if not matched_indices:
			return matched_indices

		for i in range(self.parts_len):
			rule_part = rule.parts[i]
			match_part = self.parts[i]

			index = self.match_indices[i]
			if index is None:
				continue

			result = self.parse_match(match_part, rule_part)
			matched_indices[index] = result

		return matched_indices

	def fill_matched_indices(self, matched_indices):
		if not matched_indices:
			return self

		assert self.parts is not None

		new_parts = self.parts[:]

		for i in range(self.parts_len):
			index = self.match_indices[i]
			if index is None:
				continue

			if index >= len(matched_indices):
				continue

			match_type = matched_indices[index]
			new_parts[i] = new_parts[i].format(match_type)

		return Match(new_parts, self.parts_contains, self.contains, self.equal)
