FROM nickgryg/alpine-pandas

RUN apk add chromium chromium-chromedriver

ENV USE_HEADLESS_BROWSER True
ENV CHROMEDRIVER_PATH "/usr/bin/chromedriver"

WORKDIR "/usr/workspace"



ENTRYPOINT ["/bin/sh"]
