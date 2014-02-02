import threading,fuzzer

def lol(x):
	for index,res in enumerate(x.fuzz()):
		if index == 100:
			break
		res.success()
	x.commit_to_database()

if __name__ == "__main__":
	x = fuzzer.Fuzzer()
	x.initialize()
	my_t = threading.Thread(target=lol,args=(x,))
	my_t.start()
	my_t.join()