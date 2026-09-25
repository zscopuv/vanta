from vanta import Table

table = Table("Name", "Surname", "Age")

table.add_row("Peter", "Novak", 35)
table.add_row("Jozef", "Novak", 25)
table.add_rows([("Anton", "Novak", 65), ("Milos", "Novak", 45)])

table.print()