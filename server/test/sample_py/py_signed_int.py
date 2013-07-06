#!/usr/bin/env python


def create_signed_64bit_int(num):
	'''
	As per: http://stackoverflow.com/questions/7822956/how-to-convert-negative-integer-value-to-hex-in-python
	
	The value (1<<64) is one larger than will fit in a 64-bit integer. Adding it to a negative number will turn
	it positive, as long as the negative number fits in 64 bits. If the original number was positive, the % will
	undo the effect of the addition
	'''
	nbits = 64
	nbit_mask = (1 << nbits)

	return (num + (1 << nbits)) % (1 << nbits)

def convert_toSigned64bitInt(num):
	nbit = 64
	start_num = (1 << (nbit-1))
	new_num = num - start_num
	return new_num


# -9,223,372,036,854,775,808
# 0b1000000000000000000000000000000000000000000000000000000000000000
min_neg_64bit_int = -9223372036854775808

# 9,223,372,036,854,775,807
# 0b111111111111111111111111111111111111111111111111111111111111111
max_pos_64bit_int = 9223372036854775807

a_neg = create_signed_64bit_int(min_neg_64bit_int)
a_pos = create_signed_64bit_int(max_pos_64bit_int)

# Output of min 64 bit will
print "# Mask"
mask = 2**64 - 1
print mask
print bin(mask)

print "# Min 64 bit"
print a_neg
print bin(a_neg)
print bin(1 << 63)

print "# Max 64 bit"
print a_pos
print bin(a_pos)


print "# CONVERT"
test_num=9255716238278000640
#test_num=10
a_num = convert_toSigned64bitInt(test_num)
print a_num
print bin(abs(a_num))