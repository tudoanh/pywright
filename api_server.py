import uvicorn
from playwright.async_api import async_playwright

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class URL(BaseModel):
    url: str


# create a view that take POST request contain url param, and return the html
# @app.route("/scrape", methods=["POST"])
@app.post("/scrape")
async def scrape(url: URL):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.goto(url.url)
        html = await page.content()
        await browser.close()
        return HTMLResponse(content=html, status_code=200)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
