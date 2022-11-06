FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./sso.py .
EXPOSE 5555
CMD [ "python", "./sso.py" ]