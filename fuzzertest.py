import Fuzzer

def main():
	fuzz_instance = Fuzzer.Fuzzer()
	fuzz_instance.initialize()
	i = 0
	for result in fuzz_instance.fuzz():
		if i == 255:
			break
		print result.value
		i += 1

if __name__ == "__main__":
	main()
