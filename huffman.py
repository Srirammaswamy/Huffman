#!/usr/local/bin/python3
import os
import sys
import argparse
import shutil
import struct
import heapq
from collections import defaultdict


FrequencyMap = defaultdict(int)
EncodedMap = dict()
DecodedMap = dict()
delimiter = '|'


class Node:
	def __init__(self, char, freq):
		self.char = char
		self.freq = freq
		self.right = None
		self.left = None
	
	def __gt__(self, other):
		if self.freq > other.freq:
			return True
		if self.freq == other.freq:
			if self.char > other.char:
				return True
		return False

	def __lt__(self, other):
		if self.freq < other.freq:
			return True
		if self.freq == other.freq:
			if self.char < other.char:
				return True
		return False

	def __eq__(self, other):
		if(other == None):
			return False
		if(not isinstance(other, Node)):
			return False
		if self.freq == other.freq:
			return True
		return False

	def __str__(self):
		return "{}: {}".format(self.freq, self.char)

	def __repr__(self):
		return "{}: {}".format(self.freq, self.char)


def addElements(node1, node2):
	newNode = Node('', node1.freq+node2.freq)
	newNode.left = node1
	newNode.right = node2
	return newNode


def traverse(node, char):
	global EncodedMap
	assert char in EncodedMap.keys(), 'Char {} not found in EncodedMap.keys()'.format(char)
	if node.char == char:
		return ''


def binaryToString(value, zero_padding=False):
	if zero_padding:
		return f'{bin(value)[2:]:0>8}'
	else:
		return f'{bin(value)[2:]}'


def binaryToChar(binary_string):
	n = int('0b'+binary_string, 2)
	c = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
	return c


def createEncodedMap(node, prefix=''):
	global EncodedMap
	if node == None:
		return
	if node.char != '':
		EncodedMap[node.char] = prefix
	createEncodedMap(node.left, prefix+'0')
	createEncodedMap(node.right, prefix+'1')


def strToBytes(data):
	b = bytearray()
	for i in range(0, len(data), 8):
		b.append(int(data[i:i+8], 2))
	return bytes(b)


def encode(input_file, output_file):
	global FrequencyMap, EncodedMap, DecodedMap
	print("encoding ", input_file, output_file)

	if not os.path.exists(input_file):
		return False

	with open(input_file, 'r') as input_fp, open(output_file, 'wb') as output_fp:
		input_buffer = input_fp.read()
		if len(input_buffer) == 0:
			return False

		# Creating frequency Map
		for byte_char in input_buffer:
			FrequencyMap[byte_char] = FrequencyMap[byte_char]+1
		FrequencyMap = dict(FrequencyMap)
		FrequencyMap = {k:v for k,v in sorted(FrequencyMap.items(), key=lambda item: item[1])}

		# Creating Tree
		MapList = []
		for char,freq in FrequencyMap.items():
			MapList.append(Node(char,freq))
		heapq.heapify(MapList)
		while len(MapList) > 1:
			node1 = heapq.heappop(MapList)
			node2 = heapq.heappop(MapList)
			newNode = addElements(node1, node2)
			heapq.heappush(MapList, newNode)
		createEncodedMap(MapList[0])

		# storing encoded data to a string buffer
		content_str = ''.join([EncodedMap[char] for char in input_buffer])
		dict_length = len(EncodedMap)
		zero_pad_length = 8 - len(content_str) % 8
		if zero_pad_length == 8:
			zero_pad_length = 0
		zero_pad_length_binary = f'{bin(zero_pad_length)[2:]:0>8}'
		zero_pad_binary = '0' * zero_pad_length
		content_str = content_str + zero_pad_binary
		content_str = zero_pad_length_binary + content_str

		# writing header information (EncodedMap size, keys and values) to the binary file
		output_fp.write(dict_length.to_bytes(1, byteorder='big', signed=False))
		for key in EncodedMap.keys():
			output_fp.write(key.encode())
		for value in EncodedMap.values():
			output_fp.write(value.encode())
			output_fp.write(delimiter.encode())
		
		# writing encoded data to the binary file
		output_fp.write(strToBytes(content_str))
		return True


def decode(input_file, output_file):
	global EncodedMap, DecodedMap
	print("decoding ", input_file, output_file)
	
	if not os.path.exists(input_file):
		return False

	with open(input_file, 'rb') as input_fp, open(output_file, 'w') as output_fp:
		# reading the encoded binary data
		encoded_data = ''
		byte = input_fp.read(1)
		while len(byte) > 0:
			encoded_data += f"{bin(ord(byte))[2:]:0>8}"
			byte = input_fp.read(1)

		data_length = len(encoded_data)
		if data_length < 8:
			return False # Corrupted file

		map_size_binary = encoded_data[:8]
		map_size = int(map_size_binary, base=2)
		key_list, value_list = [], []

		if data_length < map_size*8:
			return False # Corrupted file

		# parsing header section from binary data
		pos = 0
		for pos in range(1,map_size+1):
			key_binary = encoded_data[pos*8:(pos+1)*8]
			key_list.append(binaryToChar(key_binary))
		pos += 1
		delimiter_count = 0
		value_str = ''
		while(delimiter_count < map_size):
			char = binaryToChar(encoded_data[pos*8:(pos+1)*8])
			pos += 1
			if char == delimiter:
				value_list.append(value_str)			
				delimiter_count += 1
				value_str = ''
			else:
				value_str += char

		# constructing DecodedMap from header information
		DecodedMap = {v:k for k,v in zip(key_list, value_list)}

		# parsing content section (actual data) from binary data
		zero_padded_binary = encoded_data[pos*8:(pos+1)*8]
		encoded_conent = encoded_data[(pos+1)*8:]
		zero_padded_value = int(zero_padded_binary, base=2)
		if zero_padded_value > 1:
			encoded_conent = encoded_conent[:-zero_padded_value+1]
		rear, front = 0, 1 
		length = len(encoded_conent)
		decoded_data = ''
		while front < length:
			sub_str = encoded_conent[rear:front]
			if sub_str in DecodedMap.keys():
				decoded_data += DecodedMap[sub_str]
				rear = front
			front += 1
		
		# writing decoded text to a text file
		output_fp.write(decoded_data)
		return True


def get_options(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Huffman compression.")
	groups = parser.add_mutually_exclusive_group(required=True)
	groups.add_argument("-e", type=str, help="Encode files")
	groups.add_argument("-d", type=str, help="Decode files")
	parser.add_argument("-o", type=str, help="Write encoded/decoded file", required=True)
	options = parser.parse_args()
	return options


if __name__ == "__main__":
	options = get_options()
	if options.e is not None:
		encode(options.e, options.o)
	if options.d is not None:
		decode(options.d, options.o)
