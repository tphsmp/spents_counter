from datetime import datetime, timedelta
import sqlite3

# текущая дата
current_date = datetime.now().date()

name = input('Введите имя: ')

try:
    sqlite_connection = sqlite3.connect('money_count.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("SELECT * FROM spents WHERE name=?", (name,))
    data = cursor.fetchall()

    # если в таблице есть данные с указанным именем
    if data:
        # получаем максимальный id записи с указанным именем, что соответствует самой поздней записи
        [id], = cursor.execute("SELECT MAX(id) FROM spents WHERE name=?", (name,))

        # полчуаем из БД последнюю запись от имени выбранного пользователя
        cursor.execute("SELECT * FROM spents WHERE name=? AND id=?", (name, id))
        dat = cursor.fetchone()
        money_sum = dat[2]
        daily_sum = dat[3]
        totally_spent = dat[5]
        totall_economy = dat[7]
        days_overall = dat[8]
        start_date = dat[10]
        final_date = dat[11]
        days_left = dat[9]

        # предлагаем пользователю варианты действий
        decision = input('на данный момент у вас в распоряжении ' + str(money_sum) + ' \n если хотите '
                                                                                     'записать свои траты '
                                                                                     'введите да \n '
                                                                                     'если хотите просмотреть отчет о '
                                                                                     'своих тратах введите чек '
                                                                                     '\n ввод: ')

        # обработка выбора пользователя
        if decision == 'чек':
            # вывод результата выборки
            print('Вы располагаете суммой ' + str(money_sum) + '\n всего потрачено ' + str(
                totally_spent) + '\n сэкономлено ' + str(totall_economy) + '\n дней осталось: ' + str(days_left))

        if decision == 'нет':
            quit()

        if decision == 'да':
            date = input('Укажите дату в формате (гггг-мм-дд), введите today чтобы начать с сегодняшней даты: ')

            if date == 'today':
                date = current_date

            else:
                date = datetime.strptime(date, '%Y-%m-%d').date()

            day_spent = input('Введите сумму, потраченную ' + str(date) + ': ')
            day_spent = int(day_spent)

            totally_spent = totally_spent + day_spent
            dayly_economy = daily_sum - day_spent
            totall_economy = totall_economy + dayly_economy
            money_sum = money_sum - day_spent
            final_date = datetime.strptime(final_date, '%Y-%m-%d').date()
            days_left = final_date - current_date
            days_left = days_left.days

            print('*********************************************')

            if str(start_date) == str(date):
                # выбираем данные из последней записи для ее обновления
                cursor.execute("SELECT * FROM spents WHERE name=? and id=?", (name, id))
                dat = cursor.fetchone()
                current_money_sum = dat[2]
                current_daily_sum = dat[3]
                current_daily_spent = dat[4]
                current_totally_spent = dat[5]
                current_total_economy = dat[7]
                current_days_overall = dat[8]
                current_final_date = dat[11]

                money_sum = current_money_sum - day_spent
                dayly_spent = current_daily_spent + day_spent
                totally_spent = current_totally_spent + day_spent
                dayly_economy = daily_sum - dayly_spent
                total_economy = current_total_economy - day_spent

                cursor.execute(
                    f"UPDATE spents SET money_sum=?, daily_spent=?, totally_spent=?, daily_economy=?, "
                    f"total_economy=?, days_left=? WHERE id={id}",
                    (money_sum, dayly_spent, totally_spent, dayly_economy, total_economy, days_left))
                sqlite_connection.commit()
            else:

                insert = """INSERT INTO spents (name, money_sum, daily_sum, daily_spent, totally_spent, daily_economy, 
                                                       total_economy, days_overall, days_left, start_date, finish_date, 
                                                       record_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_tupple = (
                    name, money_sum, daily_sum, day_spent, totally_spent, dayly_economy, totall_economy,
                    str(days_overall), days_left, str(date), str(final_date), str(current_date))
                execute = cursor.execute(insert, data_tupple)
                sqlite_connection.commit()

    # если по указанному имени совпадений не найдено
    if not data:
        decision = input('Похоже что вы еще не делали никаких записей, хотите продолжить? ')
        if decision == 'да':
            money_sum = input('Введите сумму: ')
            date = input(
                'Укажите начальную дату в формате (гггг-мм-дд) или введите today чтобы начать с сегодняшней даты: ')
            if date == 'today':
                date = current_date
            else:
                date = datetime.strptime(date, '%Y-%m-%d').date()

            days_overall = input('Укажите количество дней: ')
            final_date = date + timedelta(int(days_overall))
            daily_sum = int(money_sum) // int(days_overall)

            print('Вы располагаете суммой ' + money_sum + ' которую хотели бы потратить за ' + days_overall
                  + 'дней в период с ' + str(date) + ' по ' + str(final_date) +
                  '\n В среднем вы имеете возможность тратить по ' + str(daily_sum) + ' в день \n')

            sqlite_insert_query = """INSERT INTO spents (name, money_sum, daily_sum, daily_spent, totally_spent, 
            daily_economy, total_economy, days_overall, days_left, start_date, finish_date, record_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            data_tupple = (
                name, money_sum, daily_sum, 0, 0, 0, 0, days_overall, 0, str(date), str(final_date), str(current_date))

            execute = cursor.execute(sqlite_insert_query, data_tupple)
            sqlite_connection.commit()
            further_action = input('Чтобы продолжить введите да, для отмены нажмите нет: ')

            if further_action == 'да':
                date_input = input('Укажите дату (гггг-мм-дд) или по умолчанию можем использовать текущую дату: ')
                if date_input == 'today':
                    date_input = str(date)

                [id], = cursor.execute("SELECT MAX(id) FROM spents WHERE name=?", (name,))

                daily_spent = input('Укажите сумму, которую вы потратили ' + date_input + ': ')
                cursor.execute("SELECT * FROM spents WHERE name=? and id=?", (name, id))
                dat = cursor.fetchone()
                money_sum = dat[2]
                daily_sum = dat[3]
                #totall_economy = dat[7]
                days_overall = dat[8]
                final_date = dat[11]
                totally_spent = dat[5]

                daily_economy = daily_sum - int(daily_spent)
                totall_economy = daily_economy
                money_sum = money_sum - int(daily_spent)
                totally_spent = totally_spent + int(daily_spent)
                final_date = datetime.strptime(final_date, '%Y-%m-%d').date()
                days_left = final_date - current_date
                days_left = days_left.days

                cursor.execute(
                    f"UPDATE spents SET money_sum=?, daily_spent=?, totally_spent=?, daily_economy=?, "
                    f"total_economy=?, days_left=? WHERE id={id}",
                    (money_sum, daily_spent, totally_spent, daily_economy, totall_economy, days_left))
                sqlite_connection.commit()

            else:
                print('BYE')
        else:
            print('BYE')
    cursor.close()
except sqlite3.Error:
    print(Exception)

