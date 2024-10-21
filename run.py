from aviation.data import Data

try:
    with Data() as bot:
        bot.landing_page()
        bot.extract_data()
except Exception as e:
    print(e)