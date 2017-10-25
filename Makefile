lint:
	pylint --rcfile=.pylintrc teriaki worker app.py -f parseable -r n && \
	pycodestyle teriaki worker app.py --max-line-length=120 && \
	pydocstyle teriaki worker app.py

test: lint
	py.test --verbose --color=yes tests.py
