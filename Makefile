.PHONY: demo test validate

demo:
	python3 scripts/run_demo.py

test:
	python3 -m unittest discover -s tests -v

validate: test
	python3 scripts/run_demo.py --quiet
