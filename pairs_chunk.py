from constants import UNASSIGNED_USER

USER_NAME = "USER_NAME"
STARTING_ROW = "STARTING_ROW"
END_ROW = "END_ROW"

PAIRS_CHUNK_COLUMNS = {
    USER_NAME: 0,
    STARTING_ROW: 1,
    END_ROW: 2,
}


class PairsChunk:
    def __init__(self, sheet, row_index_in_db):
        self.row_index_in_db = int(row_index_in_db)
        self.sheet = sheet
        self.row = sheet.row_values(row_index_in_db)
        self.owner = self.row[PAIRS_CHUNK_COLUMNS[USER_NAME]]
        self.start_row_index = int(self.row[PAIRS_CHUNK_COLUMNS[STARTING_ROW]])
        self.end_row_index = int(self.row[PAIRS_CHUNK_COLUMNS[END_ROW]])

    def update_owner(self, user_name):
        print(f"updating: ", self.row_index_in_db, self.start_row_index)
        assert(self.owner == UNASSIGNED_USER)
        self.owner = user_name
        self.sheet.update_cell(self.row_index_in_db, PAIRS_CHUNK_COLUMNS[USER_NAME] + 1, self.owner)

    def chunk_still_available(self):
        self.row = self.sheet.row_values(self.row_index_in_db)
        self.owner = self.row[PAIRS_CHUNK_COLUMNS[USER_NAME]]
        return self.owner == UNASSIGNED_USER
