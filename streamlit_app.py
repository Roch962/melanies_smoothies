import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title and instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your smoothie will be: **{name_on_order}**")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    # Clean and format the list of ingredients
    unique_ingredients = list(dict.fromkeys(ingredients_list))  # Preserve order and remove duplicates
    ingredients_string = ", ".join(unique_ingredients)  # Combine the ingredients list as a clean string

    # Display selected ingredients
    st.subheader("You selected the following ingredients:")
    st.write(ingredients_string)

    # Loop through selected fruits and fetch their SEARCH_ON values
    for fruit_chosen in unique_ingredients:
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"The search value for **{fruit_chosen}** is **{search_on_value}**.")

    # Display SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.subheader("SQL Statement Preview:")
    st.code(my_insert_stmt, language="sql")

    # Submit button to insert the order
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie with {ingredients_string} has been ordered, {name_on_order}!", icon="✅")
