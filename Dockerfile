FROM python:3

RUN pip3 install redis	

COPY cached_echo.py /
EXPOSE 65432

ENTRYPOINT ["python", "cached_echo.py"]