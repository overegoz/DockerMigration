bars = 50

print("<msg1>")
msg1 = "Hello world\n"
print("msg1 length : ", len(msg1))  # len = 12
print(msg1)
print("-" * bars, "\n")

print("<msg2>")
msg2 = msg1.strip()
print("msg2 length : ", len(msg2))  # len = 11 (마지막 개행문자 제거)
print(msg2)
print("-" * bars, "\n")

print("<msg3>")
msg3 = "Hello world! My name is Taewoon"
delimeter = ' '
msg3_words = msg3.split(delimeter)
print("msg3_words has ", len(msg3_words), " words : ")
for word in msg3_words:
	print(word)
print("-" * bars, "\n")