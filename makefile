PYTHON=/usr/bin/python3.6
NPM=/usr/bin/npm

.ONESHELL:
all:
	cd ./frontend
	$(NPM) run dev
	cd ../backend
	$(PYTHON) main.py

install:
	cd frontend
	$(NPM) install

clean:
	rm result.txt
