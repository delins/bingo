#!/usr/bin/env python3

import argparse


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

from random import Random

class NumberGenerator75:
	def __init__(self):
		self.r = Random()

	def generate_grid(self):
		r = self.r
		result = []
		result.append(r.sample(range(1, 16), 5))
		result.append(r.sample(range(16, 31), 5))
		s = r.sample(range(31, 46), 4)
		result.append([s[0], s[1], None, s[2], s[3]])
		result.append(r.sample(range(46, 61), 5))
		result.append(r.sample(range(61, 76), 5))
		return result


class Card:
	LINE_CAP_DEFAULT = 0
	LINE_CAP_ROUND = 1
	LINE_CAP_SQUARE = 2
	def __init__(self, sizes, font_type, font_size, numbers=None, line_cap=LINE_CAP_SQUARE):
		self.cell_x = sizes[0]
		self.cell_y = sizes[1]
		self.start_x = sizes[2]
		self.start_y = sizes[3]
		self.line_cap = line_cap
		self.numbers = numbers or []
		self.font_type = font_type
		self.font_size = font_size
		self.font = pdfmetrics.getFont(self.font_type)

		self.x_positions = [self.start_x + i*self.cell_x for i in range(6)]
		self.y_positions = [self.start_y + i*self.cell_y for i in range(6)]

	def draw(self, canvas):
		self.draw_grid(canvas)
		self.draw_numbers(canvas)

	def draw_grid(self, canvas):
		# Store the original line cap so that we can reset it later. 
		# It's a private attribute so it's ugly, but also the only way AFAIK
		original_line_cap = canvas._lineCap
		canvas.setLineCap(self.line_cap)
		canvas.grid(self.x_positions, self.y_positions)
		canvas.setLineCap(original_line_cap)

	def draw_numbers(self, canvas):
		string = str(self.numbers[0][0])
		for c, column in enumerate(self.numbers):
			for n in range(5):
				string = str(column[n] or '')
				width, height = self._calculate_string_size(string)
				pos_x = self.x_positions[c]
				pos_y = self.y_positions[n]
				canvas.drawString(
					pos_x + 0.5*self.cell_x - 0.5*width, 
					pos_y + 0.5*self.cell_y - 0.5*height, 
					string)

	def _calculate_string_size(self, string):
		#ascent = (face.ascent * self.font_size) / 1000.0
		#descent = (face.descent * self.font_size) / 1000.0
		width = self.font.stringWidth(string, self.font_size)
		face = self.font.face
		cap_height = (face.capHeight * self.font_size) / 1000
		return width, cap_height

class Page:
	def __init__(self, output, font_type=None, font_size=10, page_size=A4):
		self.canvas = canvas.Canvas(output)
		self.page_width, self.page_height = page_size
		self.unit_size = self.page_width / 18
		self.number_generator = NumberGenerator75()
		self.font_type = font_type
		self.font_size = font_size
		self.canvas.setFont(self.font_type, self.font_size)


	def draw(self):
		u = self.unit_size
		
		sizes = [u, u, 2*u, 2*u]
		numbers = self.number_generator.generate_grid()
		card = Card(sizes, self.font_type, self.font_size, numbers, line_cap=Card.LINE_CAP_ROUND)
		card.draw(self.canvas)

		sizes = [u, u, 11*u, 2*u]
		numbers = self.number_generator.generate_grid()
		card = Card(sizes, self.font_type, self.font_size, numbers)
		card.draw(self.canvas)

		sizes = [u, u, 2*u, 12*u]
		numbers = self.number_generator.generate_grid()
		card = Card(sizes, self.font_type, self.font_size, numbers)
		card.draw(self.canvas)

		sizes = [u, u, 11*u, 12*u]
		numbers = self.number_generator.generate_grid()
		card = Card(sizes, self.font_type, self.font_size, numbers)
		card.draw(self.canvas)

		self.canvas.showPage()

	def draw_grid(self):
		original_line_cap = self.canvas._lineCap
		self.canvas.setLineCap(2)
		self.canvas.setStrokeColor(colors.lightgrey)

		x_positions = [self.unit_size * i for i in range(19)]
		y_positions = [self.unit_size * i for i in range(19)]
		self.canvas.grid(x_positions, y_positions)
		self.canvas.setLineCap(original_line_cap)
		self.canvas.setStrokeColor(colors.black)


	def save(self):
		self.canvas.save()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--font-type',
		help='TrueType font file to use',
		required=True)
	parser.add_argument('-s', '--font-size',
		help='Font size (default=%(default)s)',
		default=10,
		type=int)
	parser.add_argument('-o', '--output',
		help='Name of output pdf file (will overwrite without asking)',
		required=True)
	args = parser.parse_args()
	if args.font_type:
		pdfmetrics.registerFont(TTFont(
			args.font_type, 
			args.font_type
		))

	p = Page(args.output, font_type=args.font_type, font_size=args.font_size)
	p.canvas.setTitle(args.output)
	p.draw_grid()
	p.draw()
	p.save()
