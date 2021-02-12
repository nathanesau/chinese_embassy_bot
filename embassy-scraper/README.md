# Embassy Scraper

Docker Instructions:

```bash
# build the image
docker build -t selenium-tests:image .

# push the image to dockerhub
docker tag selenium-tests:image nathanesau/chinese_embassy_bot:selenium-tests
docker push nathanesau/chinese_embassy_bot:selenium-tests

# run the image
docker run -d --restart=always --name=selenium-tests nathanesau/chinese_embassy_bot:selenium-tests
```