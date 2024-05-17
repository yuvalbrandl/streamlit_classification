import streamlit as st
import gspread
from streamlit import session_state as state
from single_pair import SinglePair
from users import User
from constants import *


def init_users(users_sheet):
    for user_index in range(2, TOTAL_USERS + 2):
        row = users_sheet.row_values(user_index)
        state.users.append(User(*row))


def init_state():
    """
    Initialize the state of the app.
    The function is called many times due to the streamlit nature.
    But the logic will run upon the first time the function is called only.
    """
    if INDEX not in state:
        state.index = 0
        gc = gspread.service_account_from_dict(json.loads(st.secrets["credentials"]))
        sh = gc.open("classification_DB")
        state.sheet = sh.worksheet("ClassificationSheet")
        state.users_sheet = sh.worksheet("RowsDivider")
        state.users = []
        state.current_user = None
        state.page = MAIN_PAGE
        init_users(state.users_sheet)
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
    state.current_user = [user for user in state.users
                          if user.user_name == user_name][0]
    state.index = state.current_user.start_row_index
    on_next()


def run_home_page():
    st.title("Sentence Similarity Classifier")
    user_name = st.radio("Please choose your name:",
                         [user.user_name for user in state.users])
    print("user_name", user_name)
    print(type(user_name))
    st.button("Apply", on_click=on_apply_home_page, args=(user_name,))


def get_next_pair():
    """
    Gets the next pair to label of state.current_user.
    Makes sure the pair is not labeled yet,
    and that the pair is in the user's range.
    """
    if state.index <= state.current_user.end_row_index:
        state.current_pair = SinglePair(state.sheet, state.index, LABELS)
        if int(state.current_pair.label):
            state.index += 1
            get_next_pair()


def on_next():
    """
    Handles clicks that require next pair
    :return:
    """
    get_next_pair()
    if state.index <= state.current_user.end_row_index:
        move_page_to_labeling()
    else:
        move_page_to_bye(reason="You finished labeling all your pairs")


def run_labeling_page():
    st.button("Done for today", type="primary", on_click=move_page_to_bye)
    st.title("Sentence Similarity Classifier")
    st.header("Pairs to label")
    st.write(f"index is: {state.index}")
    st.markdown(f"### Sentence A:", unsafe_allow_html=True)
    st.write(f"**{state.current_pair.sentence_a}**")
    st.markdown(f"### Sentence B:", unsafe_allow_html=True)
    st.write(f"**{state.current_pair.sentence_b}**")
    result = st.radio("What is the hierarchy of the sentences?", LABELS)
    if st.button("Submit"):
        st.write(f"For sentence a: {state.current_pair.sentence_a}  \n"
                 f"and sentence b: {state.current_pair.sentence_b}  \n"
                 f"You chose {result}")
        state.current_pair.set_label(result)
        state.current_pair.update_pair()
        st.button("Next", on_click=on_next)


def run_bye_page():
    st.title("Bye Bye")
    st.write("Thank you for labeling!")
    st.write("You can close the browser now")


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
    main()
