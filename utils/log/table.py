from prettytable import PrettyTable

def log_table_from_cols(headers: list, table: list):
    my_table = PrettyTable()
    my_table.field_names = headers

    for row in range(len(table[0])):
        my_table.add_row([table[col][row] for col in range(len(table))])
    print(my_table)

def log_table_from_rows(headers: list, table: list):
    my_table = PrettyTable()
    my_table.field_names = headers

    for row in table:
        my_table.add_row(row)
    print(my_table)
