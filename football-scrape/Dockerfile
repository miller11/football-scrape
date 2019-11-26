FROM nickgryg/alpine-pandas

RUN apk upgrade && apk add chromium chromium-chromedriver

ENV RUNNING_IN_CONTAINER True
ENV CHROMEDRIVER_PATH "/usr/bin/chromedriver"
ENV GCP_PROJECT_NAME "football-scrape"

ENV FANTASY_HTML_BUCKET "fantasy-year-html"
ENV FANTASY_DATA_BUCKET "fantasy-year-data"

ENV SAVE_HTML True


ENV START_YEAR "1992"
ENV END_YEAR "1993"

WORKDIR "/usr/workspace"

RUN mkdir -p /usr/workspace/code && mkdir -p /usr/workspace/files

COPY code/ /usr/workspace/code

COPY requirements.txt /usr/workspace

RUN pip install --upgrade pip && pip install -r requirements.txt

ENTRYPOINT ["/bin/sh"]
