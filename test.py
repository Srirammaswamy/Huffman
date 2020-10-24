import os
import unittest

from huffman import encode, decode, Node, addNodes, \
	createFrequencyMap, createEncodedMap, createPriorityQueue, \
	readBindaryData, strToBytes, binaryToChar, zeroPadAndAppendLength, toBinaryString

class TestHuffman(unittest.TestCase):
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

	def test_zeroPadAndAppendLength(self):
		assert zeroPadAndAppendLength("1") == "0000011110000000"
		assert zeroPadAndAppendLength("101") == "0000010110100000"
		assert zeroPadAndAppendLength("10101010") == "0000000010101010"
	
	def test_toBinaryString(self):
		assert toBinaryString(1, zero_padding=False) == "1"
		assert toBinaryString(5, zero_padding=False) == "101"
		assert toBinaryString(1, zero_padding=True) == "00000001"
		assert toBinaryString(5, zero_padding=True) == "00000101"

	def test_binaryToChar(self):
		assert binaryToChar("01000001") == "A"
		assert binaryToChar("00110000") == "0"

	def test_strToBytes(self):
		assert strToBytes("111") == b"\x07"
		assert strToBytes("0000000100000101") == b"\x01\x05"

	def test_readBinaryData(self):
		with open("binary_file1.bin", "wb") as fp1, open("binary_file2.bin", "wb") as fp2:
			fp1.write(strToBytes("101"))
			fp2.write(strToBytes("10000000"))
		with open("binary_file1.bin", "rb") as fp1, open("binary_file2.bin", "rb") as fp2:
			assert readBindaryData(fp1) == "00000101"
			assert readBindaryData(fp2) == "10000000"
		try:
			os.remove("binary_file1.bin")
			os.remove("binary_file2.bin")
		except OSError:
			pass
	
	def test_createFrequencyMap(self):
		string = "hello world"
		freq_dict = {' ': 1, 'd': 1, 'e': 1, 'h': 1, 'l': 3, 'o': 2, 'r': 1, 'w': 1}
		assert createFrequencyMap(string) == freq_dict

	def test_createEncodedMap_createPriorityQueue(self):
		'''
                    root
                    / \\
                   /   \\
                  a    i1
                  4    6
                  0    1
                      / \\
                     /   \\
                    i2   b
                    3    3
                    0    1
                   / \\
                  /   \\
                  d   c
                  1   2
                  0   1
		'''
		string = "aaaabbbccd"
		frequency_map = createFrequencyMap(string)
		root = createPriorityQueue(frequency_map)
		gt_encoded_map = {'a': '0', 'b': '11', 'c': '101', 'd': '100'}
		encoded_map = dict()

		assert root.left.char == 'a'
		assert root.right.right.char == 'b'
		assert root.right.left.right.char == 'c'
		assert root.right.left.left.char == 'd'

		assert createEncodedMap(encoded_map, root) == gt_encoded_map

if __name__ == '__main__':
	unittest.main()
