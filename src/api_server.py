import uvicorn
from enum import Enum
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from pydantic import BaseModel, validator

from const import LOCALES

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Device(str, Enum):
    dekstop = "Desktop Chrome"
    iphone6 = "iPhone 6"
    iphoneX = "iPhone X"
    galaxyS9 = "Galaxy S9+"
    iPad = "iPad Mini"


class Params(BaseModel):
    url: str
    device: Device = Device.dekstop
    locale: str = "en_US"
    color_scheme: str = "dark"
    capture: bool = False

    @validator("url")
    def url_must_start_with_http(cls, v):
        if not v.startswith("http"):
            raise HTTPException(
                detail="url must start with http",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return v

    @validator("device")
    def validate_device(cls, v):
        if v not in [d.value for d in Device]:
            raise HTTPException(
                detail="Invalid device", status_code=status.HTTP_400_BAD_REQUEST
            )
        return v

    @validator("locale")
    def validate_locale(cls, v):
        if v not in LOCALES.keys():
            raise HTTPException(
                detail="Invalid locale", status_code=status.HTTP_400_BAD_REQUEST
            )
        return v

    @validator("color_scheme")
    def validate_color_scheme(cls, v):
        if v not in ["dark", "light"]:
            raise HTTPException(
                detail="Invalid color scheme", status_code=status.HTTP_400_BAD_REQUEST
            )
        return v


# create a view that take POST request contain url param, and return the html
@app.post("/scrape", status_code=status.HTTP_200_OK)
async def scrape(params: Params, response: Response):
    async with async_playwright() as pw:
        try:
            browser = await pw.chromium.launch()
            context = await browser.new_context(
                **pw.devices[params.device],
                locale=params.locale,
                color_scheme=params.color_scheme,
            )
            page = await context.new_page()
            await page.goto(params.url, timeout=5000)
            html = await page.content()
            if params.capture:
                screenshot = await page.screenshot(full_page=True)
            await browser.close()
            if params.capture:
                return Response(content=screenshot, media_type="image/png")
            else:
                return HTMLResponse(content=html, status_code=200)
        except Exception as e:
            print(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Can not scrape the url"}


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
