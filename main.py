from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from rag import find_cocktails_by_ingredient, recommend_by_favorites
from memory import add_preference, get_preferences

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/ask", response_class=HTMLResponse)
async def ask(request: Request, message: str = Form(...)):
    user_id = "user123"  # replace with real user ID later
    response = ""

    if message.lower().startswith("i love "):
        ingredient = message[7:].strip()
        add_preference(user_id, ingredient)
        response = f"Got it! I’ve saved your preference: {ingredient}"
    elif message.lower().startswith("what are my favourite"):
        favs = get_preferences(user_id)
        response = f"Your favorite ingredients are: {', '.join(favs)}"
    elif "recommend" in message.lower():
        favs = get_preferences(user_id)
        response = recommend_by_favorites(favs)
    elif "containing" in message.lower():
        ingredient = message.split("containing")[-1].strip()
        response = find_cocktails_by_ingredient(ingredient)
    else:
        response = "Sorry, I didn’t understand your request."

    return templates.TemplateResponse("chat.html", {"request": request, "response": response, "message": message})
