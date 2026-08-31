.PHONY: install test html pdf render clean

install:
	python -m pip install -e '.[dev]'

test:
	pytest -q

html:
	quarto render --to html

pdf:
	quarto render --to pdf

render:
	quarto render

clean:
	rm -rf _book .quarto .pytest_cache
