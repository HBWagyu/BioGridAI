.PHONY: install test ui api

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest backend/tests -q

ui:
	streamlit run ui/streamlit_app.py --server.port 8501

api:
	uvicorn backend.app.main:app --reload --port 8000
