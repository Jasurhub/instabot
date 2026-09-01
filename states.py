from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()


class AdminState(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_location = State()
    waiting_for_location_address = State()
