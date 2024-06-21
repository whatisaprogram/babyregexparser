# babyregexparser

A regex "engine" I made to learn some basics of compilation.

Have you ever wanted a slow, bad-performing regex parser? Do you not trust those "experts" who are probably PAID to write regex? Of course not. Trust the little guy. Trust me. 

For real, this regex parser recognizes a subset of what is generally understood to be the regex language, with the following rules (R is the start symbol here):

R -> S
R -> RR
R -> R*
R -> R+
R -> R|R
R -> RS
R -> (R)
S -> any (at least ascii) character defined in the regex

Note that this language doesn't recognize some common conveniences, like the ability to just express "any alphabetic symbol" like [a-Z]. It also allows expressions such as (ab)+* and (ab)*+, which I have judged to be good enough, since the "meaning" of a regex isn't meaningfully changed by allowing them.

This regex "engine" does not use regex itself, and the parsing instead utilizes a three-lookahead approach. Next, it is filtered into a sort of atypical abstract syntax tree, and from the AST, an epsilon-NFA is created. The episilon-NFA is then filtered to eliminate the epsilon transitions and the NFA is converted into a DFA with the standard algorithm; I made very good use of python's inbuilt ability to have dictionaries have multiple data types; in this case, tuples of varying sizes.

First, import hello.py

When you call regex(regexstring), you can think of it as creating a DFA that is then used by the function check_if_valid_nonregularized to evaulate any string passed into it

dfa = regex("abc|d")
is_consistent_with_dfa = check_if_valid_nonregularized(dfa, "d")
is_consistent_with_dfa_2 = check_if_valid_nonregularized(dfa, "abd")

Once created, the DFA can be used to check if any arbitrary string fits the regular expression.

Since this isn't really production code, it's very messy, and there are a lot of things that could be refactored. For example, making my AST generator a regressive function would have saved me a lot of headaches when testing. You may also see "NFAify" in place of "DFAify", stuff like that. 

exam.py contains some of the test cases with runtime measurements. 

Thank you for reading this, random person on the internet. Have a nice day.
