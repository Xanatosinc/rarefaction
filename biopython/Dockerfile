FROM biopython/biopython

COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./generate-table.sh /app/generate-table.sh
COPY ./faToTab.py /biopython/faToTab.py

WORKDIR /biopython

ENTRYPOINT /app/entrypoint.sh
