# LICENSE: LGPL v3.0

# markdown stuff

import mistune

class IMarkdownRenderer(mistune.Renderer):
	""" renderer of markdown """
	def __init__(self):
		super().__init__()

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
		return '<img {} onerror="imageRenderer.processing(this); imageRenderer.picture.assignTo(this);">'.format(cmd)
		# return '<img {} onerror="alert(imageRenderer.processing(this));">'.format(cmd)


class IMarkdown(mistune.Markdown):
	""" ************************************************* markdown ************************************************* """
	def __init__(self):
		self.renderer = IMarkdownRenderer()
		super().__init__(renderer=self.renderer, hard_wrap=True)


def main():
	pass

if __name__ == '__main__':
	main()
