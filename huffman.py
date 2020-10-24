#!/usr/local/bin/python3
import os
import sys
import argparse
import shutil
import struct
import heapq
from collections import defaultdict

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


def addNodes(node1, node2):
	''' Add two Node elements and create a new Node. '''

	newNode = Node('', node1.freq+node2.freq)
	newNode.left = node1
	newNode.right = node2
	return newNode


def compress(input_buffer):
	''' Compress the text data to encoded binary data. '''
	
	# STEP 1: Creating a FrequencyMap for the input string buffer
	frequency_map = createFrequencyMap(input_buffer)

	# STEP 2: Creating a PriorityQueue from FrequencyMap
	root = createPriorityQueue(frequency_map)

	# STEP 3: Creating EncodedMap using PriorityQueue
	encoded_map = dict()
	encoded_map = createEncodedMap(encoded_map, root)

	# STEP 4: Storing encoded data to a string buffer
	encoded_data = ''.join([encoded_map[char] for char in input_buffer])
	encoded_data = zeroPadAndAppendLength(encoded_data)

	return encoded_map, encoded_data


def decompress(encoded_data):
	''' Decompress the encoded binary data to original text.
	
	ENCODED DATA FORMAT
	------- ---- ------
	
	`encoded_map_info` `encoded_data`

	encoded_map_info -> `map_length` `key1` `key2` `...` `value1` `delimiter` `value2` `delimiter` `...`
	encoded_data -> `pad_size` `zero_padded_encoded_data`
	
	'''

	decoded_map = dict()
	decoded_data = ''
	data_length = len(encoded_data)

	if data_length < 8:
		return decoded_map, decoded_data # Corrupted file

	# STEP 1: Decoding EncodedMap length
	map_size_binary = encoded_data[:8]
	map_size = int(map_size_binary, base=2)
	key_list, value_list = [], []

	if data_length < map_size*8:
		return decoded_map, decoded_data # Corrupted file

	# STEP 2: Decoding EncodedMap keys and values
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

	# STEP 3: Constructing DecodedMap from decoded Map Information
	decoded_map = {v:k for k,v in zip(key_list, value_list)}

	# STEP 4: Getting Huffman-encoded data and converting to binary string representation
	zero_padded_binary = encoded_data[pos*8:(pos+1)*8]
	encoded_conent = encoded_data[(pos+1)*8:]
	zero_padded_value = int(zero_padded_binary, base=2)
	if zero_padded_value > 1:
		encoded_conent = encoded_conent[:-zero_padded_value+1]
	rear, front = 0, 1 
	length = len(encoded_conent)

	# STEP 5: Decoding Huffman-encoded data from binary string
	decoded_data = ''
	while front < length:
		sub_str = encoded_conent[rear:front]
		if sub_str in decoded_map.keys():
			decoded_data += decoded_map[sub_str]
			rear = front
		front += 1

	return decoded_map, decoded_data


def readBindaryData(fp):
	''' Reading the encoded binary data. '''
	encoded_data = ''
	byte = fp.read(1)
	while len(byte) > 0:
		encoded_data += toBinaryString(ord(byte), zero_padding=True)
		byte = fp.read(1)
	return encoded_data


def toBinaryString(value, zero_padding=False):
	''' Convert 8-bit binary data to string representation. '''
	if zero_padding:
		return f'{bin(value)[2:]:0>8}'
	else:
		return f'{bin(value)[2:]}'


def binaryToChar(binary_string):
	''' Convert 8-bit binary data to corresponding utf-8 character. '''
	n = int('0b'+binary_string, 2)
	c = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
	return c


def strToBytes(data):
	''' Convert the binary string representation to binary data. '''
	b = bytearray()
	for i in range(0, len(data), 8):
		b.append(int(data[i:i+8], 2))
	return bytes(b)


def zeroPadAndAppendLength(data):
	''' Perform zero padding to the data (for last byte) and
	append the padded length value as the starting byte. '''
	zero_pad_length = 8 - len(data) % 8
	if zero_pad_length == 8:
		zero_pad_length = 0
	zero_pad_length_binary = toBinaryString(zero_pad_length, zero_padding=True)
	zero_pad_binary = '0' * zero_pad_length
	data = data + zero_pad_binary
	data = zero_pad_length_binary + data
	return data


def createFrequencyMap(input_buffer):
	''' Create frequency Map. '''
	frequency_map = defaultdict(int)
	for byte_char in input_buffer:
		frequency_map[byte_char] = frequency_map[byte_char]+1
	frequency_map = dict(frequency_map)
	frequency_map = {k:v for k,v in sorted(frequency_map.items(), key=lambda item: item[1])}
	return frequency_map


def createEncodedMap(encoded_map, node, prefix=''):
	''' Create EncodedMap from the tree. '''
	if node == None:
		return
	if node.char != '':
		encoded_map[node.char] = prefix
	createEncodedMap(encoded_map, node.left, prefix+'0')
	createEncodedMap(encoded_map, node.right, prefix+'1')
	return encoded_map


def createPriorityQueue(frequency_map):
	''' Create PriorityQueue from the FrequencyMap. '''
	MapList = []
	for char,freq in frequency_map.items():
		MapList.append(Node(char,freq))
	heapq.heapify(MapList)
	while len(MapList) > 1:
		node1 = heapq.heappop(MapList)
		node2 = heapq.heappop(MapList)
		new_node = addNodes(node1, node2)
		heapq.heappush(MapList, new_node)
	return MapList[0]


def encode(input_file, output_file):
	''' Huffman-encoding functionality. '''
	print("encoding ", input_file, output_file)

	if not os.path.exists(input_file):
		return False

	with open(input_file, 'r') as input_fp, open(output_file, 'wb') as output_fp:
		input_buffer = input_fp.read()
		if len(input_buffer) == 0:
			return False

		encoded_map, encoded_data = compress(input_buffer)
		dict_length = len(encoded_map)
		if dict_length == 0:
			return False

		# writing header information (EncodedMap size, keys and values) to the binary file
		output_fp.write(dict_length.to_bytes(1, byteorder='big', signed=False))
		for key in encoded_map.keys():
			output_fp.write(key.encode())
		for value in encoded_map.values():
			output_fp.write(value.encode())
			output_fp.write(delimiter.encode())
		
		# writing encoded data to the binary file
		output_fp.write(strToBytes(encoded_data))
		return True


def decode(input_file, output_file):
	''' Huffman-decoding functionality. '''
	print("decoding ", input_file, output_file)
	
	if not os.path.exists(input_file):
		return False

	with open(input_file, 'rb') as input_fp, open(output_file, 'w') as output_fp:

		encoded_data = readBindaryData(input_fp)
		decoded_map, decoded_data = decompress(encoded_data)
		if len(decoded_map) == 0:
			return False
		
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
