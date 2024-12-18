import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Connect to Snowflake and fetch data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert Snowpark DataFrame to Pandas
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
fruit_list = pd_df["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", fruit_list, max_selections=5
)

if ingredients_list:
    # Ensure unique and clean ingredients list
    unique_ingredients = list(dict.fromkeys(ingredients_list))  # Remove duplicates
    ingredients_string = ", ".join(unique_ingredients)  # Combine ingredients

    # Display selected fruits and their SEARCH_ON values
    st.subheader("Nutrition Information for Selected Fruits:")
    for fruit_chosen in unique_ingredients:
        # Get the SEARCH_ON value for the fruit
        search_on_value = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        # Display the search value sentence
        st.write(f"The search value for **{fruit_chosen}** is **{search_on_value}**.")

        # Mocked API Call for Nutrition Information
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_value}")
        if smoothiefroot_response.status_code == 200:
            st.subheader(f"{fruit_chosen} Nutrition Information")
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"Could not retrieve data for {fruit_chosen}.")

    # Create the SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Display SQL statement
    st.subheader("SQL Statement Preview:")
    st.code(my_insert_stmt, language="sql")

    # Submit Button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

