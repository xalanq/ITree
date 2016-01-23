# LICENSE: LGPL v3.0

# markdown stuff

import mistune, re

# Thanks https://github.com/jupyter/nbconvert/blob/master/nbconvert/filters/markdown_mistune.py

class MathBlockGrammar(mistune.BlockGrammar):
	block_math = re.compile(r"^\$\$(.*?)\$\$", re.DOTALL)
	latex_environment = re.compile(r"^\\begin\{([a-z]*\*?)\}(.*?)\\end\{\1\}",
												re.DOTALL)


class MathBlockLexer(mistune.BlockLexer):
	default_rules = ['block_math', 'latex_environment'] + mistune.BlockLexer.default_rules

	def __init__(self, rules=None, **kwargs):
		if rules is None:
			rules = MathBlockGrammar()
		super(MathBlockLexer, self).__init__(rules, **kwargs)

	def parse_block_math(self, m):
		"""Parse a $$math$$ block"""
		self.tokens.append({
			'type': 'block_math',
			'text': m.group(1)
		})

	def parse_latex_environment(self, m):
		self.tokens.append({
			'type': 'latex_environment',
			'name': m.group(1),
			'text': m.group(2)
		})


class MathInlineGrammar(mistune.InlineGrammar):
	math = re.compile(r"^\$(.+?)\$", re.DOTALL)
	block_math = re.compile(r"^\$\$(.+?)\$\$", re.DOTALL)
	text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~$]|https?://| {2,}\n|$)')


class MathInlineLexer(mistune.InlineLexer):
	default_rules = ['block_math', 'math'] + mistune.InlineLexer.default_rules

	def __init__(self, renderer, rules=None, **kwargs):
		if rules is None:
			rules = MathInlineGrammar()
		super(MathInlineLexer, self).__init__(renderer, rules, **kwargs)

	def output_math(self, m):
		return self.renderer.inline_math(m.group(1))

	def output_block_math(self, m):
		return self.renderer.block_math(m.group(1))


class MarkdownWithMath(mistune.Markdown):
	def __init__(self, renderer, **kwargs):
		if 'inline' not in kwargs:
			kwargs['inline'] = MathInlineLexer
		if 'block' not in kwargs:
			kwargs['block'] = MathBlockLexer
		super(MarkdownWithMath, self).__init__(renderer, **kwargs)

	def output_block_math(self):
		return self.renderer.block_math(self.token['text'])

	def output_latex_environment(self):
		return self.renderer.latex_environment(self.token['name'], self.token['text'])


class IMarkdownRenderer(mistune.Renderer):
	""" renderer of markdown """
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def link(self, link, title, text):
		"""
		<a href="file:/xxx/xxx" title="xxx" onclick="linkRenderer.processing(this)">xxx</a>
		"""
		link = mistune.escape(link.replace('"', '&quot;')) if link else ''
		text = mistune.escape(text) if text else ''
		title = mistune.escape(title.replace('"', '&quot;')) if title else ''
		# print('<a href="{}" title="{}" onclick="linkRenderer.processing(this)">{}</a>'.format(link, title, text))

		return '<a href="{}" title="{}" onclick="linkRenderer.processing(this)">{}</a>'.format(link, title, text)

	def block_code(self, code, lang=None):
		""" lang : lang|xxx|xxx|xxx - space was replaced by ` """
		if not lang:
			return '\n<pre class="brush: plain;">{}</pre>\n'.format(mistune.escape(code))
		tokens = lang.split('|')
		lang = tokens[0]
		if lang == '':
			lang = 'plain'
		cmd = 'brush:{};'.format(lang)
		for word in tokens[1:]:
			word = word.split(':', 1)
			if len(word) == 2:
				name, value = word
				if name == 'fold':
					if value in ('0', '1'):
						cmd += 'collapse:{};'.format(('false', 'true')[int(value)])
				elif name == 'title':
					cmd += 'title:\'{}\';'.format(value.replace('`', ' '))
				elif name == 'line':
					if value in ('0', '1'):
						cmd += 'gutter:{};'.format(format(('false', 'true')[int(value)]))

		# print('\n<pre class="{}">{}</pre>\n'.format(cmd, mistune.escape(code)))
		return '\n<pre class="{}">{}</pre>\n'.format(cmd, mistune.escape(code))

	def image(self, src, title, text):
		if not src:
			return super().image(src, title, text)
		width = ''
		height = ''
		if title:
			tokens = title.split('|')
			title = tokens[0]
			for word in tokens[1:]:
				word = word.split(':', 1)
				if len(word) == 1:
					word = word[0].split('x', 1)
					if len(word) == 2:
						if word[0].isdigit() and word[1].isdigit():
							width = word[0] + 'px'
							height = word[1] + 'px'
				elif len(word) == 2:
					name, value = word
					if name == 'height':
						height = value
					if name == 'width':
						width = value
		src = mistune.escape(src.replace('"', '&quot;')) if src else ''
		text = mistune.escape(text) if text else ''
		title = mistune.escape(title.replace('"', '&quot;')) if title else ''
		cmd = ' src="#" link="{}"'.format(src)
		cmd += ' alt="{}"'.format(text) if text else ''
		cmd += ' title="{}"'.format(title) if title else ''
		cmd += ' width="{}"'.format(width) if width else ''
		cmd += ' height="{}"'.format(height) if height else ''
		# print(cmd)
		# return '<img {} onerror="alert(imageRenderer.processing(this));">'.format(cmd)
		return '<img {} onerror="imageRenderer.processing(this); imageRenderer.picture.assignTo(this);">'.format(cmd)

	# Pass math through unaltered - mathjax does the rendering in the browser
	def block_math(self, text):
		return '$$%s$$' % text

	def latex_environment(self, name, text):
		return r'\begin{%s}%s\end{%s}' % (name, text, name)

	def inline_math(self, text):
		return '$%s$' % text


class IMarkdown(mistune.Markdown):
	""" ************************************************* markdown ************************************************* """
	def __init__(self):
		self.renderer = IMarkdownRenderer()
		super().__init__(renderer=self.renderer, inline=MathInlineLexer(self.renderer), block=MathBlockLexer(), hard_wrap=True)

	def output_block_math(self):
		return self.renderer.block_math(self.token['text'])

	def output_latex_environment(self):
		return self.renderer.latex_environment(self.token['name'], self.token['text'])

def main():
	m = IMarkdown()
	print(m('abc $ a * b * c $ efg'))


if __name__ == '__main__':
	main()
