from users import User

SENTENCE_A = "sentence_a"
SENTENCE_B = "sentence_b"
USER_ID = "user_id"
LABEL = "label"
USER_NAME = "user_name"


PAIR_COLUMNS = {SENTENCE_A: 0,
                SENTENCE_B: 1,
                LABEL: 5,
                USER_NAME: 6}


class SinglePair:
    def __init__(self, sheet, row_index, valid_labels):
        self.row_index = row_index
        self.sheet = sheet
        self.row = sheet.row_values(row_index)
        self.sentence_a = self.row[PAIR_COLUMNS[SENTENCE_A]]
        self.sentence_b = self.row[PAIR_COLUMNS[SENTENCE_B]]
        self.label = self.row[PAIR_COLUMNS[LABEL]]
        self.valid_labels = valid_labels
        self.user_name = None

    def set_label(self, label):
        if label not in self.valid_labels:
            raise ValueError(f"Label must be one of {self.valid_labels}")
        print(f"setting to {self.valid_labels.index(label) + 1}")
        self.label = self.valid_labels.index(label) + 1

    def set_user_name(self, user_name):
        self.user_name = user_name

    def update_pair(self):
        self.sheet.update_cell(self.row_index, PAIR_COLUMNS[LABEL] + 1, self.label)
        if self.user_name:
            self.sheet.update_cell(self.row_index, PAIR_COLUMNS[USER_NAME] + 1, self.user_name)

    def is_labeled(self):
        return self.label is not None
