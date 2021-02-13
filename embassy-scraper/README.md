# Embassy Scraper

Docker Instructions:

```bash
# build the image
docker build -t embassy_scraper .

# run the image
docker run -d --restart=always --name=embassy_scraper embassy_scraper

# push to github container registry
# run using git bash
docker tag embassy_scraper docker.pkg.github.com/nathanesau/chinese_embassy_bot/embassy_scraper:1.0
docker push docker.pkg.github.com/nathanesau/chinese_embassy_bot/embassy_scraper:1.0
```
