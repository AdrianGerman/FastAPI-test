from fastapi import FastAPI, Body, Path, Query, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Any, Coroutine, Optional, List
from starlette.requests import Request
from jwt_manager import create_token
from fastapi.security import HTTPBearer
from jwt_manager import create_token, validate_token



app = FastAPI()
app.title = 'Mi primer app con FasAPI'
app.version = '0.0.1'

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request): 
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin":
            return HTTPException(status_code=403, detail="Credenciales no son validas")

class User(BaseModel):
    email: str = Field(default='admin')
    password: str = Field(default='admin')

class Movie(BaseModel):
    id: Optional[int] | None = Field(default=1)
    title: str = Field(default='Película',min_length=5, max_length=15)
    overview: str = Field(default='Descripción de la película', min_length=15, max_length=50)
    year: int = Field(default='2023', le=2023)
    rating: float = Field(examples=[3.2], ge=1.0, le=10.0)
    category: str = Field(default='Ciencia ficción', min_length=3, max_length=20)
    
    # Se ha comentado este codigo, ya que son 2 modos de hacer lo mismo que el default, pero mas
    # sencillo de editar, pero no ha funcionado como se espera, tiene un pequeño error visual,
    # estoy usando pydantic v2 y python 3.11.5
    
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "id": 1,
    #                 "title": "Película",
    #                 "overview": "Descripción de la película",
    #                 "year": 2023,
    #                 "rating": 9.0,
    #                 "category": "Ciencia ficción",
    #             }
    #         ]
    #     }
    # }
    
    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "id": 1,
    #             "title": "Película",
    #             "overview": "Descripción de la película",
    #             "year": 2023,
    #             "rating": 9.0,
    #             "category": "Ciencia ficción",
    #         }
    #     }

movies = [
    {
    "id": 1,
    "title": "Avatar",
    "overview": "Puta qué rico hehee!",
    "year": "2009",
    "rating": 7.8,
    "category": "Accion"
    },
    {
    "id": 2,
    "title": "Avatar 2",
    "overview": "Puta qué rico hehee!",
    "year": "2009",
    "rating": 7.8,
    "category": "Accion"
    }
]

@app.get('/', tags=['German'])
def message():
    return HTMLResponse('<h1>Hello world!</h1>')

@app.post('/login', tags=['auth'], status_code=200)
def login(user: User):
    if user.email == 'admin' and user.password == 'admin':
        token: str = create_token(user.dict())
        return JSONResponse(content=token, status_code=200)
    else: 
        return JSONResponse(content=['Credenciales invalidas'], status_code=401)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() ->List[Movie] :
    return JSONResponse(status_code=200, content=movies)

@app.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
def get_movies(id: int = Path(ge=1,le=2000)) -> Movie:
    filtered_movies = list(filter(lambda item: item['id'] == id, movies))
    return JSONResponse(content=filtered_movies, status_code=200) if filtered_movies else JSONResponse(
        content=["No se ha encontrado el ID de la pelicula"], status_code=404)

@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie] :
    data = [ item for item in movies if item['category'] == category ]
    return JSONResponse(content=data, status_code=200) if data else JSONResponse(
        content=["Ninguna película con dicha categoría"], status_code=404)

@app.post('/movies', tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict :
    movies.append(movie)
    return JSONResponse(content={"message": "Se ha registrado la película"}, status_code=201)

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict :
    for item in movies:
        if item["id"] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
            return JSONResponse(content={"message": "Se ha modificadop la película"}, status_code=200)
        return JSONResponse(content=["No se ha encontrado el ID de la pelicula"], status_code=404)
        
@app.delete('/movie/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int) -> dict :
    for item in movies:
        if item["id"] == id:
            movies.remove(item)
            return JSONResponse(content={"message": "Se ha eliminado la película"})
        return JSONResponse(content=["No se ha encontrado el ID de la pelicula"], status_code=404)
        

    
    