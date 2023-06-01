VENV := . venv/bin/activate &&

all:
	${VENV} python3 check_for_google_fonts.py my_domains.csv

test:
	${VENV} python3 check_for_google_fonts.py my_test.csv

init:
	python3 -m venv venv
	${VENV} pip3 install -r requirements.txt


