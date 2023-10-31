# import pandas as pd

# # Загружаем Excel файл
# xls = pd.ExcelFile('123.xlsx')

# # Получаем список названий всех листов
# sheet_names = xls.sheet_names

# # Перебираем и выводим названия листов
# for sheet_name in sheet_names:
#     print(sheet_name)

# for sheet_name in sheet_names:
#     df = pd.read_excel(xls, sheet_name=sheet_name)
#     # Здесь вы можете обрабатывать данные в df


import pandas as pd

# Загружаем Excel файл
xls = pd.ExcelFile('123.xlsx')

# Создаем пустой DataFrame, куда будем складывать результаты
result_df = pd.DataFrame()

# Перебираем каждый лист
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name='ИСП-3-5+')
    result_df = pd.concat([result_df, df], ignore_index=True)

# Убираем пустые строки
result_df = result_df.dropna(axis=0, how='all')

result_df = result_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

print(result_df)
# Теперь в result_df у вас будут все данные из всех листов без пустых строк
