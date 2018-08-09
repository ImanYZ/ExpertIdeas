print "Please enter the source file name:"
sourceFileName = raw_input()
with open(sourceFileName + '.csv', 'rb') as fr:
	with open(sourceFileName + '_Standard.csv', 'wb') as fw:
		elementNumber = 0
		commaPassed = True
		doubleQuoteObserved = False
		doubleQuoteAdded = False
		secondDoubleQuotePassed = False
		elementPhrase = ""
		for line in fr:

			line = line.replace("&amp;", "&")
			standardLine = ""

			for c in line:
				if not commaPassed:
					if doubleQuoteAdded:
						if c == ',':
							standardLine += '"'
							doubleQuoteAdded = False
							commaPassed = True
							elementPhrase = ""
							elementNumber += 1
						elif ord(c) == 10 or ord(c) == 13:
							standardLine += '"'
							elementNumber = 0
							commaPassed = True
							doubleQuoteAdded = False
							elementPhrase = ""
						elif c == '"':
							print "A Double Quote observed in the middle of the non-doublequoted element: " + elementPhrase
							print "The full line: " + line
							print "The full Standard line: " + standardLine
							print "The character is: " + c + "The character code is: " + str(ord(c))
							raw_input()
					elif doubleQuoteObserved:
						if secondDoubleQuotePassed:
							if c == ',':
								secondDoubleQuotePassed = False
								doubleQuoteObserved = False
								commaPassed = True
								elementPhrase = ""
								elementNumber += 1
							elif ord(c) == 10 or ord(c) == 13:
								elementNumber = 0
								commaPassed = True
								doubleQuoteObserved = False
								secondDoubleQuotePassed = False
								elementPhrase = ""
							elif c == '"':
								secondDoubleQuotePassed = False
							else:
								print "A single Double Quote observed in the middle of the element: " + elementPhrase
								print "The full line: " + line
								print "The full Standard line: " + standardLine
								print "The character is: " + c + "The character code is: " + str(ord(c))
								raw_input()
						else:
							if c == '"':
								secondDoubleQuotePassed = True
					else:
						if c == ',':
							commaPassed = True
							elementNumber += 1
						else:
							print "Double Quote has not been observed or added, but I observed something other than a comma in the element: " + elementPhrase
							print "The full line: " + line
							print "The full Standard line: " + standardLine
							print "The character is: " + c + "The character code is: " + str(ord(c))
							raw_input()
				else:
					commaPassed = False
					if c == ',':
						commaPassed = True
						elementNumber += 1
					elif c == '"':
						doubleQuoteObserved = True
					elif ord(c) == 10 or ord(c) == 13:
						elementNumber = 0
						commaPassed = True
						doubleQuoteObserved = False
						secondDoubleQuotePassed = False
						doubleQuoteAdded = False
						elementPhrase = ""
					else:
						standardLine += '"'
						elementPhrase += '"'
						doubleQuoteAdded = True
				standardLine += c
				elementPhrase += c
			fw.write(standardLine)
			if not doubleQuoteObserved:
				print "Line Done: " + line
				elementNumber = 0
				commaPassed = True
				doubleQuoteObserved = False
				doubleQuoteAdded = False
				secondDoubleQuotePassed = False
				elementPhrase = ""
