#token = '6112966117:AAHwtt3UivMhfGc4mhupu0wvJ_lGk1K636Q'
token = '6140655358:AAFZocgWMPnYKZUu5AglUZszflH8Ky2mLt0'  # Test
admin_chat_id = ""
chat_id_logs = -4188272335
admin_id = ['5659651535', '1806719774']
ban_list = []
support = "@sasapsa"
#  RU start_lang_hand
t1: str = "Запрос"
t2: str = "Автосервисы (скоро)"
t3: str = "Неотвеченные запросы"
t4: str = "Авторизация автразборки"
t5: str = "Аккаунт авторазборки"

sm = 'Я могу искать автозапчасти у партнеров \nharcum-pahestamaser.com'
km = 'Chat - https://t.me/HarcumPahestamaser'
fm = "Вы можете управлять мной, отправив следующие команды:"

tm = '''/order - запрос на поиск запчастей
/quick - быстрый запрос (только для авторизированных)
/disassembly - авто в разборе
/feedback - обратная связь
/language - смена языка
/login - авторизация/регистрация авторазборки'''

tms = '''/order - запрос на поиск запчастей
/quick - быстрый запрос (только для авторизированных)
/disassembly - авто в разборе
/feedback - обратная связь
/language - смена языка
/account - учетная запись моей авторазборки'''

#  AM start_lang_hand
c1: str = "Հարցում"
c2: str = "Ավտոսպասարկում (շուտով)"
c3: str = "Անպատասխան հարցումներ"
c4: str = "Թույլտվություն ինքնահավաք"
c5: str = "ինքնահավաք հաշիվ"

sc = 'Ես կարող եմ Ավտոպահեստամասեր փնտրել գործընկերներից \nharcum-pahestamaser.com'
fc = 'Դուք կարող եք կառավարել ինձ ՝ ուղարկելով հետևյալ հրամանները:'

cm = '''/order - ավտոպահեստամասերի որոնման հարցում
/quick - արագ հարցում (միայն լիազորված օգտվողների համար)
/disassembly - Ավտոն վերլուծության մեջ է։
/feedback - հետադարձ կապ
/language - լեզուն փոխելը զրուցարանում
/login - ինքնահավաքման գրանցում '''

cms = '''/order - ավտոպահեստամասերի որոնման հարցում
/quick - արագ հարցում (միայն լիազորված օգտվողների համար)
/disassembly - Ավտոն վերլուծության մեջ է։
/feedback - հետադարձ կապ
/language - լեզուն փոխելը զրուցարանում
/account - հաշվապահական հաշվառում'''

#
#
# ORDER
#
#


#  RU order_hand
ru_cc = 'Выберите авто'

ru_message = 'ОК, с маркой определились'
ru_model_message = 'Давай теперь укажем модель автомобиля'
ru_change = 'Выберите из списка:'
ru_other_mark = '"Подозреваю, что ваш автомобиль имеет одну из этих марок"'
ru_other_brnd = 'Не вижу моей модели в списке'

ru_aa = 'Отлично, теперь я знаю марку и модель вашего автомобиля'
ru_ba = 'Нужно еще указать год выпуска'
ru_ca = 'Выберите из указанного списка'

ru_year = 'Введите год выпуска:'
ru_accept = 'Принял'
ru_auto_name = "Введите название модели авто:"
ru_cool = 'Ясно, ваше авто '
ru_met = "Выберете метод заполнения информации об авто."
ru_met_1 = "БЫСТРЫЙ, Отправить фото CТС"
ru_met_2 = "ОБЫЧНЫЙ, Ввести данные вручную"
ru_photo = "Отправь мне фото CТС на котором чётко видна информация об авто."

ru_year_start = ' года выпуска'
ru_ed = 'Введите объем двигателя:'
ru_ep = 'Введите мощность двигателя:'
ru_st = 'л.с.'
ru_cb = 'Выберите кузов'
ru_at = 'Выберите коробку переключения передач'
ru_et = 'Выберите тип двигателя'
ru_d = 'Выберите привод автомобиля'
ru_code = 'Укажите код двигателя, если необходимо'
ru_ec = 'Введите код двигателя:'
ru_codes = 'Укажите код кузова, если необходимо'
ru_pt = 'Введите название запчасти, уточните о вашем авто, если необходимо'
ru_pt_photo = 'Отправьте фото запчасти'
ru_bc = 'Введите код кузова:'
ru_col = 'Замечательно!'
ru_ya = 'Теперь я все знаю о вашем авто'
ru_bcc = 'Код кузова:'
ru_ecc = 'Код двигателя:'
ru_sad = 'Автомобиль на разборах не найден, попробуйте найти запчасть в другом поколении автомобиля'
ru_sup = 'Поздравляю!'
ru_vr = 'Вы разбираете автомобиль'
ru_vu = 'Вы уже разбираете этот автомобиль'

#  AM order_hand
am_cc = 'Ընտրեք ավտո'

am_message = 'Լավ, ապրանքանիշի հետ որոշել են'
am_model_message = 'Եկեք հիմա Նշենք մեքենայի մոդելը'
am_change = 'Ընտրեք ցուցակից:'
am_other_mark = "Կասկածում եմ, որ ձեր մեքենան ունի այս ապրանքանիշերից մեկը"
am_other_brnd = 'Չեմ տեսնում իմ մոդելը ցուցակում'

am_aa = 'Հիանալի է, Հիմա ես գիտեմ ձեր մեքենայի մակնիշը և մոդելը'
am_ba = 'Դուք դեռ պետք է նշեք թողարկման տարին'
am_ca = 'Ընտրեք նշված ցուցակից'

am_year = 'Մուտքագրեք թողարկման տարին:'
am_accept = 'Ընդունել է'
am_auto_name = "Մուտքագրեք մեքենայի մոդելի անունը:"
am_cool = 'Պարզ է, ձեր մեքենան '
am_year_start = ' թողարկման տարեթիվը'
am_ed = 'Մուտքագրեք շարժիչի ծավալը:'
am_ep = 'Մուտքագրեք շարժիչի հզորությունը:'
am_st = 'ձիաւժ'
am_cb = 'Ընտրեք մարմինը'
am_at = 'Ընտրեք փոխանցման տուփը'
am_et = 'Ընտրեք Շարժիչի տեսակը'
am_d = "Ընտրեք մեքենայի սկավառակ"
am_code = 'Անհրաժեշտության դեպքում նշեք շարժիչի կոդը'
am_ec = 'Մուտքագրեք շարժիչի կոդը:'
am_codes = 'Անհրաժեշտության դեպքում նշեք մարմնի կոդը'
am_pt = 'Մուտքագրեք պահեստամասի անվանումը, անհրաժեշտության դեպքում ստուգեք ձեր մեքենայի մասին'
am_pt_photo = ""
am_bc = 'Մուտքագրեք մարմնի կոդը:'
am_col = 'Հրաշալի!'
am_ya = 'Հիմա ես ամեն ինչ գիտեմ ձեր մեքենայի մասին'
am_bcc = 'Մարմնի կոդ:'
am_ecc = 'Շարժիչի կոդ:'
am_sad = 'Մեքենան չի գտնվել ապամոնտաժման մեջ, Փորձեք գտնել մեքենայի մեկ այլ սերնդի պահեստամասեր'
am_sup = 'Շնորհավորում եմ:'
am_vr = 'Դուք ապամոնտաժում եք մեքենան'
am_vu = 'Դուք արդեն ապամոնտաժում եք այս մեքենան'
am_met = "Ընտրեք մեքենայի մասին տեղեկատվությունը լրացնելու եղանակը:"
am_met_1 = "Արագ, ուղարկել STS լուսանկար"
am_met_2 = "Նորմալ, մուտքագրեք տվյալները ձեռքով"
am_photo = "Ուղարկեք ինձ STS-ի լուսանկար, որի վրա մեքենայի մասին տեղեկատվությունը հստակ տեսանելի է:"

#
#
# REG
#
#

ru_a = 'Вы не вошли в аккаунт'
ru_b = 'Выберете способ входа в аккаунт авторазборки'
ru_c = 'Выберите тип аккаунта:'
ru_dd = 'Введите логин(без пробелов):'
ru_e = 'Введите пароль(без пробелов):'
ru_f = 'Пользователь с таким логином уже существует!'
ru_g = "Регистрация успешна!"
ru_h = 'Введите название:'
ru_i = 'Введите адрес авторазборки:'
ru_j = '''Введите номер телефона авторазборки
       по примеру +3749879877852:'''
ru_k = 'Введите описание:'
ru_l = 'Вы вышли из учетной записи'
ru_m = 'Введите новый логин:'
ru_na = 'Вы сменили логин с '
ru_nb = 'на'
ru_o = 'Введите новый пароль:'
ru_pa = 'Вы сменили пароль с '
ru_pb = 'на'
ru_r = 'Редактирование авторазборки'

am_a = 'դուք մուտք չեք գործել հաշիվ'
am_b = 'Ընտրեք ավտոմատ հավաքման հաշիվ մուտք գործելու եղանակը'
am_c = 'Ընտրեք Հաշվի տեսակը:'
am_dd = 'Մուտքագրեք մուտք (առանց բացատների):'
am_e = 'Մուտքագրեք գաղտնաբառը (առանց բացատների):'
am_f = 'Նման մուտքի օգտագործող արդեն գոյություն ունի:'
am_g = "Գրանցումը հաջող է:"
am_h = 'Մուտքագրեք անունը:'
am_i = "Մուտքագրեք ավտոմատ հավաքման հասցեն:"
am_j = 'Մուտքագրեք ավտոմատ հավաքման հեռախոսահամարը' \
       'օրինակով +3749879877852:'
am_k = 'Մուտքագրեք նկարագրությունը:'
am_l = 'Դուք դուրս եք եկել հաշվից'
am_m = 'Մուտքագրեք նոր մուտք:'
am_na = 'Դուք փոխել եք մուտքը'
am_nb = '-ից'
am_o = 'Մուտքագրեք նոր գաղտնաբառ:'
am_pa = 'Դուք փոխել եք գաղտնաբառը '
am_pb = '-ից'
am_r = 'Ինքնահավաքման խմբագրում'
