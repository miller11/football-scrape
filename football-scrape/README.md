# Football Scrape

This is a simple set of python programs to scrape and store data from www.pro-football-reference.com. 


### Installation

* `pip3 install -r requirements.txt`
* Download a version of chromedriver compatible with your version of chrome and save it `/Users/rhmiller/chromedriver`

### Running

* Set environment variable `CHROMEDRIVER_PATH` 
    * for container = `export CHROMEDRIVER_PATH=/usr/bin/chromedriver`
    * for local dev = `export CHROMEDRIVER_PATH=/user/local/bin/chromedriver`
    
    
* Containers also need to set `USE_HEADLESS_BROWSER` for headless browser (we get some better performance locally w/o it set)


### Docker Stuff 
Build the docker container
`docker build -t py_scrape .`

To run the container with the GCloud stuff you must use the GCloud CLI to login 
`gcloud auth application-default login`

Running Docker container (including copying in GCloud creds)
`docker run -it -v=$HOME/.config/gcloud:/root/.config/gcloud py_scrape:latest`