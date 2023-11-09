import typing as t

def format_table(headers: t.List[str], rows: t.List[t.List[str]]) -> str:
    """ """

    def fmt_row(row: t.List[str]) -> str:
        cols: t.List[str] = []
        for i, h in enumerate(row):
            if i == 0:
                cols.append(f"{h:<30}")
            elif i == len(headers) - 1:
                cols.append(f"{h:^15}")
            else:
                cols.append(f"{h:^15}")
        return "".join(cols)

    table: t.List[str] = []

    table.append(fmt_row(headers))
    sep = "=" * len(table[0])
    table.append(sep)

    # Iterate over the list of strings and create table rows
    for row in rows:
        table.append(fmt_row(row))

    table.append(sep)

    return "\n".join(table)
