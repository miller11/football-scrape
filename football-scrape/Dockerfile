FROM nickgryg/alpine-pandas

RUN apk upgrade && apk add chromium chromium-chromedriver

ENV RUNNING_IN_CONTAINER True
ENV CHROMEDRIVER_PATH "/usr/bin/chromedriver"
ENV GCP_PROJECT_NAME "football-scrape"

ENV HTML_BUCKET "pfr-html-files"
ENV FANTASY_DATA_BUCKET "fantasy-year-data"

ENV SAVE_HTML True
ENV GET_FRESH_HTML False


ENV START_YEAR "1992"
ENV END_YEAR "1993"

WORKDIR "/usr/workspace"

RUN mkdir -p /usr/workspace/code && mkdir -p /usr/workspace/files

COPY code/ /usr/workspace/code

COPY requirements.txt /usr/workspace

RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["/bin/sh"]
