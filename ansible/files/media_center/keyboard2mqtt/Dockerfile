FROM python:3.15.2
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD main.py /keyboard2mqtt.py
CMD ["python", "-u", "/keyboard2mqtt.py"]
