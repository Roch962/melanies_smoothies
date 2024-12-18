import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title and Instructions
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Input for Smoothie Name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your smoothie will be: **{name_on_order}**")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch Data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect for Ingredients
fruit_list = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Display Selected Fruits and Nutrition Info
if ingredients_list:
    # Remove duplicates and convert to title case for consistency
    unique_ingredients = list(set(ingredients_list))  # Remove duplicates
    ingredients_string = ", ".join([ingredient.title() for ingredient in unique_ingredients])  # Title case

    # Display the selected ingredients
    st.subheader("You selected the following ingredients:")
    st.write(ingredients_string)

    # Loop through each selected fruit and display SEARCH_ON and Nutrition Info
    st.subheader("Nutrition Information for Selected Fruits:")
    for fruit_chosen in unique_ingredients:
        # Get the SEARCH_ON value for the selected fruit
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display the search value sentence
        st.write(f"The search value for **{fruit_chosen.title()}** is **{search_on_value}**.")

        # Mocked API Call for Nutrition Information (adjust if API is available)
        nutrition_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_value}")
        if nutrition_response.status_code == 200:
            nutrition_data = nutrition_response.json()
            st.write(f"**{fruit_chosen.title()} Nutrition Information:**")
            st.dataframe(nutrition_data, use_container_width=True)
        else:
            st.write(f"Could not retrieve data for {fruit_chosen.title()}.")

    # Display SQL Insert Statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.subheader("SQL Statement Preview:")
    st.code(my_insert_stmt, language="sql")

    # Submit Button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your smoothie with {ingredients_string} has been ordered, {name_on_order}!", icon="✅")
