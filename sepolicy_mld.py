class MultiLevelDict:
	def __init__(self):
		self.d = {}

	def add(self, rule):
		d = self.d

		for part in rule.parts:
			if rule.parts[-1] is part:
				d = d.setdefault(part, [])

				if rule not in d:
					d.append(rule)
			else:
				d = d.setdefault(part, {})

	def _remove(self, d, i, rule):
		part = rule.parts[i]
		if part not in d:
			return

		if isinstance(d[part], dict):
			self._remove(d[part], i + 1, rule)
		elif isinstance(d[part], list) and rule in d[part]:
			d[part].remove(rule)

		if not len(d[part]):
			d.pop(part)

	def remove(self, rule):
		return self._remove(self.d, 0, rule)

	def _walk_and_do_list(self, d, match, do_fn, *args):
		for r in d:
			if not match.match_rule_parts_contains(r):
				continue

			if not match.match_rule_varargs(r):
				continue

			do_fn(r, *args)

	def _walk_and_do(self, d, match, level, do_fn, *args):
		for k in d:
			if not match.match_part_index(k, level):
				continue

			if isinstance(d[k], list):
				self._walk_and_do_list(d[k], match, do_fn, *args)
			else:
				self._walk_and_do(d[k], match, level + 1, do_fn, *args)

	def _do_get(self, rule, *args):
		results = args[0]
		results.append(rule)

	def get(self, match):
		results = []
		self._walk_and_do(self.d, match, 0, self._do_get, results)
		return results

	def get_one(self, match):
		results = self.get(match)
		if not len(results):
			return None
		return results[0]

	def __str__(self):
		return json.dumps(self.d, indent=4, default=str)
