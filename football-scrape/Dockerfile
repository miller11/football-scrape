FROM nickgryg/alpine-pandas

RUN apk add chromium chromium-chromedriver

ENV RUNNING_IN_CONTAINER True
ENV CHROMEDRIVER_PATH "/usr/bin/chromedriver"
ENV GCP_PROJECT_NAME "football-scrape"

ENV FANTASY_HTML_BUCKET "fantasy-year-html"
ENV FANTASY_DATA_BUCKET "fantasy-year-data"


ENV START_YEAR = 1992
ENV END_YEAR = 1993

WORKDIR "/usr/workspace"



ENTRYPOINT ["/bin/sh"]
