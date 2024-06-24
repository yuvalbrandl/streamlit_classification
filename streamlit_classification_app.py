import streamlit as st
import gspread
from streamlit import session_state as state
from single_pair import SinglePair
from users import User
from pairs_chunk import PairsChunk
from constants import *
from collections import deque
import traceback


def init_chunk(user_index):
    """
    Initialize a chunk (a continues range of pairs that a
    single users should tag) from the RowsDivider sheet.
    """
    new_chunk = PairsChunk(state.users_sheet, user_index)
    user_name = new_chunk.owner
    if user_name == UNASSIGNED_USER:
        state.available_chunks.append(new_chunk)
        return
    if user_name not in state.users:  # Should create a new user
        new_user = User(new_chunk.owner, new_chunk)
        state.users[new_user.user_name] = new_user
    else:
        cur_user = state.users[user_name]
        cur_user.add_chunk(new_chunk)


def read_row_divider_db(users_sheet):
    """
    Read the RowsDivider sheet and initialize the users and their chunks.
    """
    total_chunks = len(users_sheet.col_values(1)) - 1
    for user_index in range(2, total_chunks + 2):
        init_chunk(user_index)


def init_state():
    """
    Initialize the state of the app.
    The function is called many times due to the streamlit nature.
    But the logic will run upon the first time the function is called only.
    """
    if INDEX not in state:
        state.index = 0
        gc = gspread.service_account_from_dict(st.secrets.credentials)
        sh = gc.open("classification_DB_sidekick")
        state.sheet = sh.worksheet("ClassificationSheet")
        state.users_sheet = sh.worksheet("RowsDivider")
        state.users = {}
        state.available_chunks = deque()

        state.current_user = None
        state.page = MAIN_PAGE
        read_row_divider_db(state.users_sheet)
        columns_list = state.sheet.row_values(1)
        print(columns_list)


def move_page_to_home():
    state.page = MAIN_PAGE


def move_page_to_labeling():
    state.page = LABELING_PAGE


def move_page_to_bye(reason=None):
    state.page = BYE_PAGE
    if reason:
        st.subheader(f"Thanks! {reason}")


def on_apply_home_page(user_name):
    """
    Function to run when the user clicks the apply button on home page.
    It sets the current user and the starting index of the user.
    :param user_name: a unique username
    """
    state.current_user = [user for user in state.users.values()
                          if user.user_name == user_name][0]
    state.index = state.current_user.current_chunk.next_to_label_index
    on_next()


def run_home_page():
    st.title("Sentence Similarity Classifier")
    user_name = st.radio("Please choose your name:",
                         [user.user_name for user in state.users.values()])
    print("user_name", user_name)
    print(type(user_name))
    st.button("Apply", on_click=on_apply_home_page, args=(user_name,))


def get_next_pair():
    """
    Gets the next pair to label of state.current_user.
    Makes sure the pair is not labeled yet,
    and that the pair is in the user's range.
    """
    assert (state.current_user is not None)
    assert (state.current_user.current_chunk is not None)
    if state.index <= state.current_user.current_chunk.end_row_index:
        state.current_pair = SinglePair(state.sheet, state.index, LABELS)
        if int(state.current_pair.label):
            state.index += 1
            get_next_pair()
    elif state.current_user.current_chunk_index < len(
            state.current_user.chunks) - 1:
        state.current_user.current_chunk_index += 1
        state.current_user.current_chunk = state.current_user.chunks[
            state.current_user.current_chunk_index]
        state.index = state.current_user.current_chunk.start_row_index
        print(state.index)
        get_next_pair()
    else:
        state.current_user.has_more_pairs = False


def on_next(result=None):
    """
    Handles clicks that require next pair
    :return:
    """
    if result:
        state.current_pair.set_label(result)
        state.current_pair.set_user_name(state.current_user.user_name)
        state.current_pair.update_pair()
        if state.current_user.current_chunk.next_to_label_index < state.current_user.current_chunk.end_row_index:
            state.current_user.current_chunk.update_next_to_label_index(state.index + 1)
    get_next_pair()
    if state.current_user.has_more_pairs:
        move_page_to_labeling()
    else:
        move_page_to_bye(reason="You finished labeling all your pairs")


def run_labeling_page():
    st.button("Done for today", type="primary", on_click=move_page_to_bye, args=("See you next time!",))
    st.title("Sentence Similarity Classifier")
    st.header("Pairs to label")
    st.write(f"You are currently labeling pair index: {state.index}")
    st.markdown(f"### Sentence A:", unsafe_allow_html=True)
    st.write(f"**{state.current_pair.sentence_a}**")
    st.markdown(f"### Sentence B:", unsafe_allow_html=True)
    st.write(f"**{state.current_pair.sentence_b}**")
    result = st.radio("What is the hierarchy of the sentences?", LABELS, index=0)
    st.button("Submit", on_click=on_next, args=(result,))
    # if st.button("Submit"):
    #     st.write(f"You chose {result}")
    #     state.current_pair.set_label(result)
    #     state.current_pair.set_user_name(state.current_user.user_name)
    #     state.current_pair.update_pair()
    #     st.button("Next", on_click=on_next)


def label_more():
    while state.available_chunks and not state.current_user.has_more_pairs:
        new_chunk = state.available_chunks.popleft()
        if new_chunk.chunk_still_available():
            state.current_user.add_chunk(new_chunk)
            state.current_user.has_more_pairs = True
            on_next()
            move_page_to_labeling()
            return
    move_page_to_bye(reason="You finished labeling all your pairs")


def run_bye_page():
    st.title("Bye Bye")
    st.write("Thank you for labeling!")
    if state.available_chunks and not state.current_user.has_more_pairs:
        st.write("There are still plenty of pairs to label!")
        st.button("Lets label 10 more pairs!", on_click=label_more)


def main():
    """
    Main function to run the streamlit app.
    """
    init_state()
    if state.page == MAIN_PAGE:
        run_home_page()
    if state.page == LABELING_PAGE:
        run_labeling_page()
    if state.page == BYE_PAGE:
        run_bye_page()


if __name__ == '__main__':
    # try:
    main()
    # except gspread.exceptions.APIError as e:
    #     raise Exception(f"got API error {e.response.status_code} {e.response.reason} {e.response.text}\n{traceback.format_exc()}")
