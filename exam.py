from hello import regex, check_if_valid_nonregularized
import time

strr = "(d|D)arth (a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)+ the (a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)+"
start = time.time()
x = regex(strr)
end = time.time()
print(end - start)
start = time.time()
print(check_if_valid_nonregularized(x, "darth Vader the unwise"))
end = time.time()
print(end - start)
start = time.time()
print(check_if_valid_nonregularized(x, "Darth vader the unwise"))
end = time.time()
print(end - start)

#extra testing:
'''strr = "www.((a|b|c)+|d).com"
x = regex(strr)
print(check_if_valid_nonregularized(x, "www..com"))
print(check_if_valid_nonregularized(x, "www.a.com"))
print(check_if_valid_nonregularized(x, "www.b.com"))
print(check_if_valid_nonregularized(x, "www.abcabcbcbbbbbaaaaccc.com"))
print(check_if_valid_nonregularized(x, "www.&&&&&&&.com"))
print(check_if_valid_nonregularized(x, "www.abcd.com"))
print(check_if_valid_nonregularized(x, "www.d.com"))'''
'''strr = "(ab|fg)*(xyz)+|a|b|c"
x = regex(strr)
print(check_if_valid_nonregularized(x, "fgfgfgfgfgabababababababababxyzxyz"))
print(check_if_valid_nonregularized(x, "a"))
print(check_if_valid_nonregularized(x, "b"))
print(check_if_valid_nonregularized(x, "ab"))
print(check_if_valid_nonregularized(x, "xyzxyz"))
print(check_if_valid_nonregularized(x, "c"))'''
