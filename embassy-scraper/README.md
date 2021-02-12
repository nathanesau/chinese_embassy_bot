# Embassy Scraper

Docker Instructions:

```bash
# build the image
docker build -t selenium-tests:image .

# run the image
docker run -d --restart=always --name=selenium-tests selenium-tests:image

# push the image to dockerhub
docker push nathanesau/chinese_embassy_bot:tagname
```