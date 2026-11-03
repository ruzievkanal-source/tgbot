import asyncio
import logging
import sys
from decimal import Context
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey, insert, select
from sqlalchemy.orm import declarative_base, sessionmaker , Mapped, mapped_column

from rk_buttons import main_buttons

load_dotenv()


TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


class NoteState(StatesGroup):
    name = State()


@dp.message(CommandStart())
async def start_handler(message: Message):
    user = message.from_user

    with Session() as session:
        db_user = session.get(User, user.id)   # bazada bormi?
        if db_user is None:
            session.add(User(id=user.id, full_name=user.full_name))
            session.commit()
            text = f"Salom, {user.full_name}! Siz bazaga saqlandingiz ✅"
        else:
            text = f"Qaytib kelganingiz bilan, {user.full_name}! 👋"

    btn = main_buttons()

    await message.answer(
        text,
        reply_markup=btn
    )

@dp.message(F.text == "view note")
async def viewnote_handler(message: Message):
    stmt = select(Note).where.id  # SELECT * FROM user_account;

    with engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            await message.answer(row.name)


@dp.message(F.text == "new note")
async def newnote_handler(message: Message, state: FSMContext):
    await message.answer("enter your note")
    await state.set_state(NoteState.name)

@dp.message(F.text, NoteState.name)
async def save_newnote_handler(message: Message, state: FSMContext):
    user = message.from_user
    await state.update_data(name = message.text)
    data: dict = await state.get_data()
    with Session() as session:
            session.add(Note( user_id=user.id, name=data['name']))
            session.commit()
    await state.clear()
    btn = main_buttons()
    await message.answer("we saved your note", reply_markup=btn)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


# Bazaga ulanish
db_name = getenv("DB_NAME")
db_user = getenv("DB_USER")
db_pass = getenv("DB_PASSWORD")
db_host = getenv("DB_HOST")
db_port = getenv("DB_PORT")

engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

Base = declarative_base()
Session = sessionmaker(bind=engine)



# Modelni qurish
class User(Base):
     __tablename__ = "users"
     id: Mapped[int] = mapped_column(BigInteger,autoincrement=True, primary_key=True)
     full_name: Mapped[str] = mapped_column(String(255))


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
# Jadvalni yaratish
Base.metadata.create_all(engine)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())