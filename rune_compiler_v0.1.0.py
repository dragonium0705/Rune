

default_functions = ["say"]
		
def compile(source, filename_output="__0utput.s"):
	symbol_table = { 
		"pf": { 
			"def": { 
				"say": {
					"type": "fn",
					"usages": 0,
					"exist": True,
					"arg_type": ["str"]
				}
			},
			"global": {},
			"primitives": {}
		},
		"fn": [
			[ "def", "say" ]
		],
		"___Literals": []
	}
	first_pass_tokens = first_pass(source)
	print(first_pass_tokens)
	
	second_pass_items = second_pass(first_pass_tokens, symbol_table)
	print(second_pass_items)
		
	third_pass_codes = third_pass(second_pass_items, symbol_table)
	
	with open(filename_output, "w") as f:
		f.write("")
	with open(filename_output, "a") as f:
		f.write(".global main\nmain:\n")
		for line in third_pass_codes["main"]:
			f.write(line)
		f.write("\n\n")
		for fns in third_pass_codes["fn"]:
			f.write(fns)
		f.write("\n\n")
		f.write(".data\n")
		for data in third_pass_codes["data"]:
			f.write(data)
		
def first_pass(source):
	tokens = []
	debug = False
		
	current_token = ""
	line_c = 0
	nl_c = 0
	str_block = False
	for symbol in source:
		line_c += 1
			
		if symbol == "\n":
			line_c = 0
			nl_c += 1
				
		elif not str_block and symbol == "[":
			if len(current_token) != 0:
				let = back_tokenize(current_token) 
				let.append((nl_c, line_c-len(current_token)))
				tokens.append(let)
				current_token = ""
			new_token = ["[", "LBracket", (nl_c, line_c)]
			tokens.append(new_token)
				
		elif symbol == "\"":
			current_token += symbol 
			if str_block:
				str_block = False
				new_token = [current_token, "strLiteral", (nl_c, line_c-len(current_token))]
				tokens.append(new_token)
				current_token = ""
			else:
				str_block = True
					
		elif not str_block and symbol == "]":
			if len(current_token) != 0:
				let = back_tokenize(current_token) 
				let.append((nl_c, line_c-len(current_token)))
				tokens.append(let)
				current_token = ""
			new_token = ["]", "RBracket", (nl_c, line_c)]
			tokens.append(new_token)
				
		elif not str_block and symbol == ";":
			if len(current_token) != 0:
				let = back_tokenize(current_token) 
				let.append((nl_c, line_c-len(current_token)))
				tokens.append(let)
				current_token = ""
			new_token = [";", "statementBreaker", (nl_c, line_c)]
			tokens.append(new_token)
		
		elif not str_block and symbol == ":":
			if len(current_token) != 0:
				let = back_tokenize(current_token) 
				let.append((nl_c, line_c-len(current_token)))
				tokens.append(let)
				current_token = ""
			new_token = [":", "colon", (nl_c, line_c)]
			tokens.append(new_token)
				
		else:
			current_token += symbol 
				
			
		if debug:
			print(f"{current_token} == {nl_c} == {line_c}")
		
	return tokens
		
		
		
		
def second_pass(tokens,symbol_table):
	all_data = []
	nest_tracker = []
	parse_token = []
	ignore = False
		
	usages = {}
		
	for token in tokens:
		definition = token[1]
		print(f"{definition} == {token[0]}")
			
		if definition == "Identity":
			parse_token.append(token)
			
		elif definition == "LBracket":
			nest_tracker.append(token)
			parse_token.append(token)
			
		elif definition == "RBracket":
			parse_token.append(token)
			if nest_tracker[-1][1] == "LBracket":
				nest_tracker.pop()
			else:
				ignore = True
					
		elif definition.endswith("Literal"):
			parse_token.append(token)
			if definition.startswith("str") and token[0][1:-1] not in symbol_table["___Literals"] :
				symbol_table["___Literals"].append([token[0][1:-1], "str"])
			
		elif definition == "colon":
			parse_token.append(token)	
				
		elif definition == "statementBreaker":
			if len(nest_tracker) == 0:
				all_data.append(attention(parse_token,symbol_table))
				parse_token = []
				
	return all_data
		
		
		
def attention(tokens_to_parse, symbol_table):
	hashmap = { "type": None }
	for index, token in enumerate(tokens_to_parse):
		if token[1] == "Identity":
			if token[0] in symbol_table["pf"].keys() and index == 0 :
				hashmap["pf"] = token[0]
				hashmap["type"] = "pfRefer"
				
			elif hashmap["type"] =="pfReferExtend" and token[0] in symbol_table["pf"][hashmap["pf"]].keys():
				 hashmap["type"] = "pfUseItem"
				 hashmap["item"] = token[0]
				
		elif token[1] == "colon":
			if hashmap["type"] == "pfRefer":
				hashmap["type"] = "pfReferExtend"
				
		elif token[1] == "LBracket":
			if hashmap["type"] == "pfUseItem" and symbol_table["pf"][hashmap["pf"]][hashmap["item"]]["type"] == "fn":
				hashmap["type"] = "fnCallRequest"
				symbol_table["pf"][hashmap["pf"]][hashmap["item"]]["usages"] += 1
				hashmap["args"] = [ None for x in range( len(symbol_table["pf"][hashmap["pf"]][hashmap["item"]]["arg_type"] ) )]
				
		elif token[1].endswith("Literal"):
			if hashmap["type"] == "fnCallRequest":
				if symbol_table["pf"][hashmap["pf"]][hashmap["item"]]["arg_type"][0] == token[1][:-7]:
					hashmap["args"][0] = [token[0], symbol_table["pf"][hashmap["pf"]][hashmap["item"]]["arg_type"][0]]
					
		elif token[1] == "RBracket":
			if hashmap["type"] == "fnCallRequest":
				hashmap["type"] = "fnCall"
					
	return hashmap 
			
		
def back_tokenize(token):
	if token.endswith("L"):
		try:
			int(token[:-1])
			return [token[:-1], "largeLiteral"]
		except ValueError:
			pass
			
	elif token.endswith("f"):
		try:
			float(token[:-1])
			return [token[:-1], "floatLiteral"]
		except ValueError:
			pass
		
	try:
		if float(token) == int(token):
			return [token, "intLiteral"]
		else:
			return [token, "doubleLiteral"]
	except ValueError :
		if token == "false":
			return [token, "booleanLiteral"]
		elif token == "true":
			return [token, "booleanLiteral"]
			
		elif token in ("none", "null", "void"):
			return ["void", "booleanLiteral"]
			
		else:
			return [token, "Identity"]
			
			
def third_pass(datas, symbol_table):
	give_writings = {"fn":[], "data":[], "main":[] }
	for liter in symbol_table["___Literals"]:
		print(liter)
		if liter[1] == "str":
			give_writings["data"].append( f"	___{liter[0].replace(' ', '_')}__{liter[1]}___: .ascii \"{liter[0]}\"\n")
			give_writings["data"].append( f"	___{liter[0].replace(' ', '_')}__{liter[1]}__length___: .quad {len(liter[0])}\n")
	
	for funcs in symbol_table["fn"]:
		my_str = ""
		
		if funcs[0] == "def":
			my_str = default_fn(funcs[1])
			
		give_writings["fn"].append( my_str )
		
		
	for data in datas:
		my_str = ""
		if data["type"] == "fnCall":
			from_pf = data["pf"]
			fn_name = data["item"]
			args = data["args"]
			if args[0][1] == "str":
				my_str+=f"	adr x10, ___{args[0][0][1:-1].replace(' ', '_')}__str___\n	adr x0, ___{args[0][0][1:-1].replace(' ', '_')}__str__length___\n	ldr x11, [x0]\n"
			
			my_str += f"	bl {from_pf}_{fn_name} \n"
			
		give_writings["main"].append(my_str)
		
	give_writings["main"].append("\n\n	mov x0, #0\n	mov x8, #93\n	svc #0")
			
			
	return give_writings
			
			
def default_fn(func_name):
	if func_name == "say":
		my_str = """def_say:
	mov x0, #1
	mov x1, x10
	mov x2, x11
	mov x8, #64
	svc #0
	
	ret
"""
	return my_str
