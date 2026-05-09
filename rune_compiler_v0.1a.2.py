class RuneCompileAarch64:
	def __init__(self, filepath, output="__0utput.s", debug=False):
		self.chars = []
		self.chars.extend(chr(ord('a') + i) for i in range(26))
		self.chars.extend(str(i) for i in range(10))
		self.chars.extend(chr(ord('A') + i) for i in range(26))
		self.__version__ = "0.1a.2"
		self.symbols = {
			"pf": {
				"def": {
					"say": { "type": "fn", "usages": 0, "exist": True, "args": ["str"] }
				},
				"global": {},
				"rune": {
					"int": { "type": "type_keyword", "usages": 0, "exist": True, "args": [] },
					"str": { "type": "type_keyword", "usages": 0, "exist": True, "args": ["int", "length"] }
				}
			},
			"id": [],
			"___literals": {},
			"___preserved_keywords": ["fn", "def", "pf", "rune"],
			"___primitives": { "str": ["rune"], "int": ["rune"] }
		}
		self.pairs = {"leftSBracket": ["rightSBracket"] }
		self.debug = debug
		with open(filepath, "r") as f:
			content = f.read()
			if self.debug:
				print(content)
			
		first_pass  = self.lexer(content)
		if self.debug:
			print("\nLexer Phase: <<")
			for i in first_pass:
				print(i)
			print(">>\n\n\nParsing: <<")
		second_pass = self.parser(first_pass)
		if self.debug:
			print(">>\n\nParser Phase: <<")
			for i in second_pass:
				print(i)
			print(">>\n\nAll Literals: <<")
			for i in self.symbols["___literals"]:
				print(f"{i} == {self.symbols['___literals'][i]}")
			print(">>\n")
			
		if self.debug:
			with open("symbol_table.json", "w") as f:
				import json
				json.dump(self.symbols, f, indent=4)
		last_pass   = self.code_gen(second_pass)
		
		
		with open(output, "w") as f:
			f.write("")
		with open(output, "a") as f:
			f.write(".global main\n main:\n")
			for i in last_pass["main"]:
				f.write(i)
			f.write("\n\n	mov x0, #0\n	mov x8, #93\n	svc #0\n\n")
			for i in last_pass["fn"]:
				f.write(f"{i}\n")
			f.write("\n\n\n.data\n")
			for i in last_pass["data"]:
				f.write(i)
		
	def id_generator(self):
		import random
		result = []
		for i in range(16):
			result.append(random.choice(self.chars))
		while "".join(result) in self.symbols["id"]:
			result = []
			for  i in range(16):
				result.append(random.choice(self.chars))
				
		self.symbols["id"].append("".join(result))
		return "".join(result)
		
	def lexer(self, source):
		tokens = []
		
		current_token = ""
		line_c = 0
		nl_c = 0
		str_block = False
		for symbol in source:
			line_c += 1
			
			if symbol == "\n":
				line_c = 0
				nl_c += 1
				if str_block:
					current_token += symbol
				
			elif symbol == ":":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
						ctoken = [ ":", "colon", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
				
				
			elif symbol == "[":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ "[", "leftSBracket", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
				
			elif symbol == "\"":
				if str_block:
				    str_block = False
				    ctoken = [current_token, "strLiteral", (nl_c, line_c - len(current_token)-1)]
				    current_token = ""
				    tokens.append(ctoken)
				else:
				    str_block = True
				
			elif symbol == "]":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ "]", "rightSBracket", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
				
			elif symbol == ";":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ ";", "semicolon", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
					
			elif symbol == "=":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ "=", "equal", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
					
			elif symbol == ".":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ ".", "dot", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
					
			elif symbol == "+":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
					ctoken = [ "+", "add", (nl_c, line_c) ]
					tokens.append(ctoken)
				else:
					current_token += symbol 
				
			elif symbol == " ":
				if not str_block:
					if len(current_token.strip()) != 0:
						back_token = self.back_tokenize(current_token)
						back_token.append( (nl_c, line_c - len(current_token) -1 ) )
						tokens.append(back_token)
						current_token = ""
				else:
					current_token += symbol 
				
			else:
				current_token += symbol

		return tokens
			
			
	def back_tokenize(self, token):
		try:
			if float(token) == int(token):
				return [ int(token), "intLiteral" ]
			else:
				return [ float(token), "floatLiteral"]
		except:
			if token == "true":
				return [ True, "booleanLiteral" ]
			elif token == "false":
				return [ False, "booleanLiteral" ]
			elif token in ("void", "null", "none"):
				return [ None, "voidLiteral" ]
			else:
				return [ token, "Identity"]
				
	def parser(self, all_tokens):
		to_parse = []
		id_y = [0]
		all_data = []
		nest_tracker = []
		ignore = False
		for token in all_tokens:
			definition = token[1]
			if self.debug:
				print(token)
			
			if definition in ( "Identity", "colon", "equal", "dot" ) or definition[-7:] == "Literal":
				to_parse.append(token)
				
			elif definition in ( "leftSBracket", "leftParenths", "leftCBracket" ):
				to_parse.append(token)
				nest_tracker.append(definition)
				
			elif definition in ( "rightSBracket", "rightParenths", "rightCBracket" ):
				to_parse.append(token)
				if len(nest_tracker) != 0:
					if nest_tracker[-1][-8:] == definition[-8:]:
						nest_tracker.pop()
					
			elif definition == "semicolon":
				if len(nest_tracker) == 0:
					info = self.attention(to_parse)
					
					if info["type"] != "invalid":
						all_data.append(info)
					else:
						print("invalid")
					to_parse = []
			
		return all_data
					
	def attention(self, all_tokens):
		info = {"type": "¿none?", "pf":"global", "referVoid": False, "value":None}# standard prefix is always global
		reparse = []
		trigger = None
		reparse_bool = False
		nest_tracker = []
		if self.debug:
			print("\n\nAttention: <<")
		
		for token in all_tokens:
			definition = token[1]
			
			if self.debug:
				print(token)
	
			if definition == "Identity":
				if reparse_bool:
					reparse.append(token)
				else:
					if info["type"] == "¿none?":
						if token[0] in self.symbols["pf"].keys():
							info["type"] = "¿pf?"
							info["pf"] = token[0]
							
						elif token[0] in self.symbols["___primitives"].keys():
							if len(self.symbols["___primitives"][token[0]]) == 1:
								info["type"] = "¿mkVar?"
								info["as"] = token[0]
								info["pf_type"] = self.symbols["___primitives"][token[0]][0]
							else:
								return {"type":"invalid"}
							
						else:
							if token[0] in self.symbols["pf"][info["pf"]].keys():
								info["type"] = "¿item?"
								info["item"] = token[0]
							else:
								info["referVoid"] = True
								info["type"] = "¿item?"
								info["item"] = token[0]
								
					elif info["type"] == "pfFrom":
						if token[0] not in self.symbols["pf"][info["pf"]].keys():
							info["referVoid"] = True
						
						if self.symbols["pf"][info["pf"]][token[0]]["type"] == "type_keyword":
							info["pf_type"] = info["pf"]
							info["pf"] = "global"
							info["type"] = "¿mkVar?"
							info["as"] = token[0]
						else:
							info["type"] = "¿item?"
							info["item"] = token[0]
							
					elif info["type"] == "¿mkVar?":
						info["type"] = "mkVar"
						info["item"] = token[0]
							
			elif definition == "colon":
				if reparse_bool:
					reparse.append(token)
				else:
					if info["type"] == "¿pf?":
						
						info["type"] = "pfFrom"
			
			elif definition in ("leftParenths", "leftCBracket", "leftSBracket"):
				if reparse_bool:
					nest_tracker.append(definition)
					reparse.append(token)
				else:
					reparse_bool = True
					trigger = token
					
					if info["type"] == "¿item?":
						if definition == "leftSBracket":
							
							if self.symbols["pf"][info["pf"]][info["item"]]["type"] == "fn":
								info["type"] = "¡fnCall!"
								info["args"] = [None for _ in range(len( self.symbols["pf"][info["pf"]][info["item"]]["args"] ))]
							else:
								return {"type":"invalid"}
								
					elif info["type"] == "¿type_input?":
						if definition == "leftSBracket":
							if len(self.symbols["pf"][info["pf_type"]][info["as"]]["args"]) != 0:
								info["type"] = "type_input"
								info["type_args"] = [None for _ in range(len(self.symbols["pf"][info["pf_type"]][info["as"]]["args"]))]
							
			elif definition in ("rightCBracket", "rightParenths", "rightSBracket"):
				if reparse_bool:
					if len(nest_tracker) >= 1:
						if nest_tracker[-1][-8:] == definition[-8:]:
							nest_tracker.pop()
						else:
							return {"type": "invalid"}
							
					elif len(nest_tracker) == 0:
						if definition in self.pairs[trigger[1]]:
							reparse_bool = False
							my_info = self.attention(reparse)
							if my_info["type"] == "invalid":
								return {"type": "invalid"}
							reparse = []
							
							if info["type"] == "¡fnCall!":
								if definition == "rightSBracket":
									info["type"] = "fnCall"
									if isinstance(my_info, list):
										info["args"] = my_info
									elif isinstance(my_info, dict):
										info["args"][0] = my_info
										
							elif info["type"] == "type_input":
								if definition == "rightSBracket":
									info["type"] = "¿mkVar?"
									if isinstance(my_info, list):
										info["type_args"] = my_info
									elif isinstance(my_info, dict):
										info["type_args"][0] = my_info
						else:
							return {"type": "invalid"}
					else:
						return {"type":"invalid"}
			
			elif definition.endswith("Literal"):
				if reparse_bool:
					reparse.append(token)
				else:
					if info["type"] == "¿none?":
						info["type"] = definition
						info["item"] = token[0]
						
					elif info["type"] == "¿initVar?":
						info["type"] = "initVar"
						info["value"] = token[0]
						
			elif definition == "equal":
				if reparse_bool:
					reparse.append(token)
				else:
					if info["type"] == "mkVar":
						info["type"] = "¿initVar?"
						
			elif definition == "dot":
				if reparse_bool:
					reparse.append(token)
				else:
					if info["type"] == "¿mkVar?":
						info["type"] = "¿type_input?"
		info = self.organizer(info)
		
		if self.debug:
			print(f"Attention output: {info}")
			print(">>\n")
		return info
		
	def organizer(self, info):
		if info["type"] in ("fnCall"):
			self.symbols["pf"][info["pf"]][info["item"]]["usages"] += 1
			
		elif info["type"].endswith("Literal"):
			if info["type"].startswith("str"):
				if info["item"] not in self.symbols["___literals"]:
					id = self.id_generator()
					self.symbols["___literals"][info["item"]] = {"type": "str", "id": id}
					
		elif info["type"] in ("mkVar", "initVar"):
			if info["item"] not in self.symbols["pf"][info["pf"]]:
				self.symbols["pf"][info["pf"]][info["item"]] = { "type": "variable", "usages": 0, "exist": True, "var_type": (info["pf_type"], info["item"]), "value": info["value"] }
			else:
				if self.symbols["pf"][info["pf"]][info["item"]]["exist"]:
					pass
				else:
					self.symbols["pf"][info["pf"]][info["item"]]["exist"] = True
			self.symbols["pf"][info["pf"]][info["item"]]["usages"] += 1
			
		return info

	def code_gen(self, all_tokens):
		writes = {"main": [], "data": [], "fn": []}
		
		for literal, body in self.symbols["___literals"].items():
			if body["type"] == "str":
				writes["data"].append(f"	____{body['id']}: .asciz \"{literal.replace("\n", "\\n")}\"\n")
				writes["data"].append(f"	____{body["id"]}__length: .quad {len(literal)}\n")
				
		for pfs, body in self.symbols["pf"].items():
			for fns, items in body.items():
				if pfs== "def":
					writes["fn"].append(self.defaults(fns))
					
		for token in all_tokens:
			if token["type"] == "fnCall":
				pf = token["pf"]
				item = token["item"]
				my_args = []
				offset = 0
				for n, i in enumerate(self.symbols["pf"][pf][item]["args"]):
					print(token["args"])
					if token["args"][n]["type"].endswith("Literal"):
						if i == "str":
							writes["main"].append(f"	adr x{10+offset}, ____{self.symbols['___literals'][token['args'][n]['item']]['id']}\n")
							writes["main"].append(f"	adr x9, ____{self.symbols['___literals'][token['args'][n]['item']]['id']}__length\n")
							offset+=1
							writes["main"].append(f"	ldr x{10+offset}, [x9]\n")
					elif token["args"][n]["type"] == "¿item?":
						if i == "str":
							if self.symbols["pf"][token["pf"]][token["item"]]["exist"]:
								print("here")
								writes["main"].append(f"	adr x{10+offset}, {token['args'][n]['pf']}__{token['args'][n]['item']}\n")
								writes["main"].append(f"	adr x9, {token['args'][n]['pf']}__{token['args'][n]['item']}__length\n")
								offset+=1
								writes["main"].append(f"	ldr x{10+offset}, [x9]\n")
							else:
								break
							
				writes["main"].append(f"	bl {pf}_{item}\n")
				
			
			elif token["type"] in ("mkVar","initVar"):
				pf = token["pf"]
				item = token["item"]
				value = token["value"]
				type = token["as"]
				pf_type = token["pf_type"]
				type_args = token.get("type_args", [0] )
				
				
				if not self.symbols["pf"][pf_type][type]["exist"]:
					continue 
				if pf_type == "rune":
					writes["data"].append(self.rune_types(type, item, value, pf, type_args))
		
		return writes
		
	def rune_types(self, type, item, value, pf, type_args):
		if type == "int":
			if value is None:
				return f"	{pf}__{item}: .quad 0\n"
			else:
				return f"	{pf}__{item}: .quad {value}\n"
		elif type == "str":
			if value is None:
				if len(type_args) != 0 and isinstance(type_args[0], dict):
					print(type_args[0])
					return f"	{pf}__{item}: .space {type_args[0]['item']}\n	{pf}__{item}__length: .quad 0\n"
				else:
					return f"	{pf}__{item}: .space 256\n	{pf}__{item}__length: .quad 0\n"
			else:
				if len(type_args) != 0 and isinstance(type_args[0], dict):
					return f"	{pf}__{item}:\n		.asciz \"{value}\"\n		.space {type_args[0]['item'] - len(value)}\n	{pf}__{item}__length: .quad {len(value)}\n"
				else:
					return f"	{pf}__{item}: .asciz \"{value}\"\n	{pf}__{item}__length: .quad {len(value)}\n"
		
	def defaults(self, fnName):
		if fnName == "say":
			return """def_say:
	mov x0, #1
	mov x1, x10
	mov x2, x11
	mov x8, #64
	svc #0
	
	ret
"""
		return ""
		
	def sym(self):
		return self.symbols

supported = {"aarch64": RuneCompileAarch64 }




if __name__ == "__main__":
	import os
	import subprocess 
	
	home = os.path.expanduser("~")
	running = True
	while running:
		line_input = input("\n\ncommand:\n\t")
		tokens = line_input.split()
		
		if tokens[0] == "comp" or tokens[0] == "compile":
			try:
				file = tokens[1]
			except IndexError:
				file = "main.rune"
				
			try:
				output = tokens[2]
			except IndexError :
				output = "__0utput.s"
				
			uname_result = subprocess.run(["uname", "-m"],capture_output=True, text=True)
			if uname_result.stdout.strip() in supported.keys():
				leftover = supported[uname_result.stdout.strip()](file, output).sym()
				
			else:
				print(f"Your current device assembly: {uname_result.stdout.strip()} is not supported\nOnly supported assembly is {[x for x in supported.keys()]}")
				
		elif tokens[0] == "run":
			try:
				output = tokens[1]
			except IndexError :
				output = "__0utput.s"
			try:
				subprocess.run([ "gcc", "-o", f"{home}/main", output ])
				result = subprocess.run([f"{home}/main"], capture_output=True, text=True)
				print(f"return code:\t{result.returncode}\n")
				print(f"output: \n{result.stdout}\n")
				print(f"output error:\n{result.stderr}\n")
			except Exception as e:
				print(f"Error:\n\t{e}")
			
		elif tokens[0] == "comprun":
			try:
				file = tokens[1]
			except IndexError:
				file = "main.rune"
				
			try:
				output = tokens[2]
			except IndexError :
				output = "__0utput.s"
				
			uname_result = subprocess.run(["uname", "-m"],capture_output=True, text=True)
			if uname_result.stdout.strip() in supported.keys():
				leftover = supported[uname_result.stdout.strip()](file, output).sym()
				
			else:
				print(f"Your current device assembly: {uname_result.stdout.strip()} is not supported\nOnly supported assembly is {[x for x in supported.keys()]}")
				
				
			try:
				subprocess.run([ "gcc", "-o", f"{home}/main", output ])
				result = subprocess.run([f"{home}/main"], capture_output=True, text=True)
				print(f"return code:\t{result.returncode}\n")
				print(f"output: \n{result.stdout}\n")
				print(f"output error:\n{result.stderr}\n")
			except Exception as e:
				print(f"Error:\n\t{e}")
				
		elif tokens[0] == "show":
			try:
				file = tokens[1]
			except IndexError:
				file = "main.rune"
				
			with open(file, "r") as f:
				print(f"\n{file} 's code:\n{f.read()}")
				
		elif tokens[0] == "showout":
			try:
				output = tokens[1]
			except IndexError :
				output = "__0utput.s"
				
			with open(output, "r") as f:
				print(f"\n{output} 's code:\n{f.read()}")