from constants import UNASSIGNED_USER
from app_api_utils import read_row_values

USER_NAME = "USER_NAME"
STARTING_ROW = "STARTING_ROW"
END_ROW = "END_ROW"
NEXT_TO_LABEL_INDEX = "NEXT_TO_LABEL_INDEX"

PAIRS_CHUNK_COLUMNS = {
    USER_NAME: 0,
    STARTING_ROW: 1,
    END_ROW: 2,
    NEXT_TO_LABEL_INDEX: 3,
}


class PairsChunk:
    def __init__(self, sheet, row_index_in_db):
        self.row_index_in_db = int(row_index_in_db)
        self.sheet = sheet
        self.row = read_row_values(sheet, self.row_index_in_db)
        # self.row = sheet.row_values(row_index_in_db)
        self.owner = self.row[PAIRS_CHUNK_COLUMNS[USER_NAME]]
        self.start_row_index = int(self.row[PAIRS_CHUNK_COLUMNS[STARTING_ROW]])
        self.end_row_index = int(self.row[PAIRS_CHUNK_COLUMNS[END_ROW]])
        next_to_label_index = None
        if len(self.row) > PAIRS_CHUNK_COLUMNS[NEXT_TO_LABEL_INDEX]:
            next_to_label_index = int(self.row[PAIRS_CHUNK_COLUMNS[NEXT_TO_LABEL_INDEX]])
        self.next_to_label_index = self.start_row_index if next_to_label_index is None else next_to_label_index

    def update_owner(self, user_name):
        print(f"updating: ", self.row_index_in_db, self.start_row_index)
        assert(self.owner == UNASSIGNED_USER)
        self.owner = user_name
        self.sheet.update_cell(self.row_index_in_db, PAIRS_CHUNK_COLUMNS[USER_NAME] + 1, self.owner)

    def update_next_to_label_index(self, next_to_label_index):
        self.next_to_label_index = next_to_label_index
        self.sheet.update_cell(self.row_index_in_db, PAIRS_CHUNK_COLUMNS[NEXT_TO_LABEL_INDEX] + 1, self.next_to_label_index)

    def chunk_still_available(self):
        self.row = self.sheet.row_values(self.row_index_in_db)
        self.owner = self.row[PAIRS_CHUNK_COLUMNS[USER_NAME]]
        return self.owner == UNASSIGNED_USER
