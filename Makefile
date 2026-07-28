.PHONY: demo test validate youtube-help analysis-help

demo:
	python3 scripts/run_demo.py

test:
	python3 -m unittest discover -s tests -v

validate: test
	python3 scripts/run_demo.py --quiet

youtube-help:
	python3 scripts/collect_youtube.py --help

analysis-help:
	python3 scripts/prepare_analysis.py --help
	python3 scripts/apply_analysis.py --help
