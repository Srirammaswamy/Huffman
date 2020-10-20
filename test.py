# Test functions goes here
import os
import unittest

from huffman import encode, decode

class TestHuffman(unittest.TestCase):
	# write all your tests here
	# function name should be prefixed with 'test'

	def test_encode(self):
		assert encode("story.txt", "story.huff") == True
		assert encode("story2.txt", "story2.huff") == False
		open("empty_file.txt", "w").close()
		assert encode("empty_file.txt", "empty_file.huff") == False
		try:
			os.remove("empty_file.txt")
			os.remove("empty_file.huff")
		except OSError:
			pass

	def test_decode(self):
		assert decode("story.huff", "story_.txt") == True
		assert decode("story2.huff", "story2_.txt") == False
		open("empty_file.huff", "wb").close()
		assert encode("empty_file.huff", "empty_file_.txt") == False
		try:
			os.remove("empty_file.huff")
			os.remove("empty_file_.txt")
		except OSError:
			pass

if __name__ == '__main__':
	unittest.main()
