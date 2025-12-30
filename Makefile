install:
	pip install -r requirements.txt

lint:
	black . && flake8 .

test:
	pytest -q

run:
	streamlit run app.py

eval:
	python scripts/eval_pipeline.py
