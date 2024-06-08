from constants import UNASSIGNED_USER


class User:
    def __init__(self, user_name, chunk):
        self.user_name = user_name
        self.chunks = [chunk]
        self.current_chunk_index = 0
        self.current_chunk = chunk
        self.has_more_pairs = True

    def add_chunk(self, chunk):
        if chunk.owner == UNASSIGNED_USER:
            chunk.update_owner(self.user_name)
        assert (chunk.owner == self.user_name)
        self.chunks.append(chunk)
