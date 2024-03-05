from aiogram import Bot, Dispatcher, executor

bot = Bot('7028205605:AAEhUyp66HJWVlhpv7Ku41IExSG3V8NX7Ks')

disp = Dispatcher(bot)

if __name__ == '__main__':
    executor.start_polling(disp)
