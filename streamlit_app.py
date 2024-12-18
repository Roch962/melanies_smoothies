import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

# Get the active session and query the table
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row['FRUIT_NAME'] for row in my_dataframe.collect()]

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Concatenate selected ingredients into a string
    for fruit_chosen in ingredients_list:
        ingredients_string +=fruit_chosen + ' '
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    # Create the SQL insert statement
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    # Display the SQL statement for debugging
    st.write(my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

import requests

# st.text(smoothiefroot_response.json())

