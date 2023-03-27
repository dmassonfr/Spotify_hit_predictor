streamlit:
	-@streamlit run app/app.py

requirements:
	@pip install -r requirements.txt


fastapi:
	@uvicorn inference-api:inference --reload