from prettytable import PrettyTable, MARKDOWN

def log_table_from_cols(headers: list, table: list, file_name=''):
    my_table = PrettyTable()
    my_table.field_names = headers

    for row in range(len(table[0])):
        my_table.add_row([table[col][row] for col in range(len(table))])
    print(my_table)

    if file_name:
        my_table.set_style(MARKDOWN)
        log_to_file(log_to_file, my_table)

def log_table_from_rows(headers: list, table: list, file_name=''):
    my_table = PrettyTable()
    my_table.field_names = headers

    for row in table:
        my_table.add_row(row)
    print(my_table)

    if file_name:
        my_table.set_style(MARKDOWN)
        log_to_file(file_name, my_table)

def log_to_file(filename: str, markdown_table):
    with open(filename, "a") as f:
        f.write(markdown_table.get_string())
        f.write('\n\n')