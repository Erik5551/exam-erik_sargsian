from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session, select


class Record(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    course: str
    date: str
    payment: str
    status: str
    user_id: int


class NewRecord(SQLModel):
    course: str
    date: str
    payment: str


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    login: str = Field(unique=True)
    password: str
    email: str
    fio: str
    phone: str
    role: str | None = Field(default="user")


class UserAuth(SQLModel):
    login: str
    password: str


engine = create_engine(r'sqlite:///database.sqlite')
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')
static = StaticFiles(directory='./static')

app.mount('/static', static)


@app.get('/')
def index(request: Request):
    role = request.cookies.get('role')
    user_id = request.cookies.get('user_id')
    
    print(f"DEBUG /: role={role}, user_id={user_id}")

    if not user_id or not role:
        return RedirectResponse('/login', status_code=302)

    if role == "admin":
        return RedirectResponse('/admin', status_code=302)

    return RedirectResponse('/profile', status_code=302)


@app.get('/admin')
def admin(request: Request):
    role = request.cookies.get('role')
    user_id = request.cookies.get('user_id')
    
    print(f"DEBUG /admin: role={role}, user_id={user_id}")
    
    if role != "admin" or not user_id:
        return RedirectResponse('/login', status_code=302)

    with Session(bind=engine) as session:
        s = select(Record, User).where(Record.user_id == User.id)
        records = session.exec(s).all()

    return templates.TemplateResponse(
        request,
        'admin.html',
        { "records": records }
    )


@app.get('/profile')
def profile(request: Request):
    role = request.cookies.get('role')
    user_id = request.cookies.get('user_id')
    
    print(f"DEBUG /profile: role={role}, user_id={user_id}")
    
    if not user_id or role == "admin":
        return RedirectResponse('/login', status_code=302)

    with Session(bind=engine) as session:
        s = select(Record).where(Record.user_id == int(user_id))
        records = session.exec(s).all()

    return templates.TemplateResponse(
        request,
        'profile.html',
        { "records": records }
    )


@app.get('/logout')
def logout():
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('user_id')
    response.delete_cookie('role')
    return response


@app.get('/create')
def create(request: Request):
    role = request.cookies.get('role')
    user_id = request.cookies.get('user_id')
    
    if role == "admin" or not user_id:
        return RedirectResponse('/login', status_code=302)
    
    return templates.TemplateResponse(request, 'create.html')


@app.post('/create')
def create_process(request: Request, new_record: Annotated[NewRecord, Form()]):
    user_id = request.cookies.get('user_id')
    
    if not user_id:
        return RedirectResponse('/login', status_code=302)

    with Session(bind=engine) as session:
        session.add(Record(
            user_id=int(user_id),
            course=new_record.course,
            payment=new_record.payment,
            date=new_record.date,
            status="Новая"
        ))
        session.commit()

    return RedirectResponse('/profile', status_code=302)


@app.post('/update/{update_id}')
def update_process(request: Request, update_id: int, status: Annotated[str, Form()]):
    role = request.cookies.get('role')
    
    if role != "admin":
        return RedirectResponse('/login', status_code=302)
    
    with Session(bind=engine) as session:
        s = select(Record).where(Record.id == update_id)
        record: Record = session.exec(s).one()
        record.status = status
        session.add(record)
        session.commit()
        session.refresh(record)

    return RedirectResponse('/admin', status_code=302)


@app.get('/register')
def register(request: Request):
    return templates.TemplateResponse(request, 'register.html')


@app.post('/register')
def register_process(request: Request, user: Annotated[User, Form()]):
    print(f"DEBUG: Регистрация пользователя {user.login}")
    with Session(bind=engine) as session:
        try:
            session.add(user)
            session.commit()
            print(f"DEBUG: Пользователь {user.login} успешно создан")
        except IntegrityError:
            session.rollback()
            print(f"DEBUG: Ошибка - логин {user.login} уже существует")
            return templates.TemplateResponse(
                request,
                'register.html',
                { "error": "Логин уже существует" }
            )

    return RedirectResponse('/login', status_code=302)


@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@app.post('/login')
def login_process(request: Request, user_auth: Annotated[UserAuth, Form()]):
    print(f"DEBUG: Попытка входа - логин: {user_auth.login}")

    # ========== ПРОВЕРКА АДМИНИСТРАТОРА ПО ЗАДАНИЮ ==========
    if user_auth.login == 'Admin26' and user_auth.password == "Demo20":
        with Session(bind=engine) as session:
            s = select(User).where(User.login == "Admin26")
            admin_user = session.exec(s).one_or_none()
            
            if not admin_user:
                admin_user = User(
                    login="Admin26",
                    password="Demo20",
                    email="admin@passazhiry.ru",
                    fio="Администратор системы",
                    phone="8(999)000-00-00",
                    role="admin"
                )
                session.add(admin_user)
                session.commit()
                session.refresh(admin_user)
                print(f"DEBUG: Создан админ в БД, id={admin_user.id}")
            
            response = RedirectResponse('/admin', status_code=302)
            response.set_cookie(key='user_id', value=str(admin_user.id))
            response.set_cookie(key='role', value='admin')
            print(f"DEBUG: Админ вошёл, установлены куки user_id={admin_user.id}, role=admin")
            return response
    # ========== КОНЕЦ ПРОВЕРКИ ==========

    # Обычная проверка для пользователей
    with Session(bind=engine) as session:
        s = select(User).where(User.login == user_auth.login).where(User.password == user_auth.password)
        user: User | None = session.exec(s).one_or_none()
        
        if not user:
            print(f"DEBUG: Пользователь {user_auth.login} не найден или неверный пароль")
            return templates.TemplateResponse(
                request,
                'login.html',
                { "error": "Неверный логин или пароль" }
            )

        print(f"DEBUG: Пользователь найден: {user.login}, id={user.id}, role={user.role}")
        
        response = RedirectResponse('/profile', status_code=302)
        response.set_cookie(key='user_id', value=str(user.id))
        response.set_cookie(key='role', value=user.role)
        
        print(f"DEBUG: Куки установлены: user_id={user.id}, role={user.role}")
        return response