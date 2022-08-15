# Cloudfire

Cloudfire is a reverse proxy to bypass cloudflare's javascript challenge (I'm under attack mode) using playwright.

## How it works

Cloudfire uses playwright to solve cloudflare challenges and stores the cookies internally (redis can also be used). It then uses those cookies for further requests using aiohttp. Whenever the response returns a 503/403 status, it uses playwright to again solve the challenge and the cycle continues.

## Installation

```sh
git clone https://github.com/lonely-code-cube/cloudfire
cd cloudfire
pip install -r requirements.txt
playwright install firefox
```

## Starting the server

```
uvicorn main:app
```

By default the server will run at port 8000.

## Usage

### Endpoints
```/get```

Method: ```POST```

Post body:

```
url: The url to make a get request
```