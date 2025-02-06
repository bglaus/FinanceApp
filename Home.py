import streamlit as st
import utils.streamlit_util as streamlit_util

def init():
    streamlit_util.init()

def draw():
    st.header("Home")

def main():
    init()
    draw()

if __name__ == "__main__":
    main()
