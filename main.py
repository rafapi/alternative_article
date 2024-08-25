from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def extract_html_after_removing_script(html_content: str) -> str:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Find and remove the specific script tag
    script_tag = soup.find("script", text=lambda text: text and "window.main();" in text)
    if script_tag:
        script_tag.extract()

    # Find the <html> tag
    html_tag = soup.find("html")

    if html_tag:
        # Return the string representation of the HTML from <html> onwards
        return str(html_tag)
    else:
        # Return a message if no <html> tag is found
        return "No <html> tag found in the HTML content."


@app.post("/extract-content")
def extract_content(url: str = Form(...)):
    # parsed_url = urlparse(url)
    # formatted_url = parsed_url.netloc + parsed_url.path

    base_url = "https://webcache.googleusercontent.com/search?q=cache:"
    # full_url = base_url + formatted_url + "&strip=0&vwsrc=0"
    full_url = base_url + url

    try:
        response = requests.get(full_url, headers=HEADERS)

        if response.status_code == 200:
            html_content = response.text
            modified_html_content = extract_html_after_removing_script(html_content)
            return HTMLResponse(modified_html_content)
        else:
            return HTMLResponse(
                f"Failed to fetch content, status code: {response.status_code}",
                status_code=response.status_code,
            )
    except requests.RequestException as e:
        return HTTPException(f"Error fetching the page: {e}", status_code=400)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse('static/index.html')
