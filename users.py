class User:
    def __init__(self, user_name, id, start_row_index, end_row_index):
        self.user_name = user_name
        self.id = int(id)
        self.start_row_index = int(start_row_index)
        self.end_row_index = int(end_row_index)

